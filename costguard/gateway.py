"""LLM gateway: the single choke point CostGuard uses to account for every
token and every dollar an agent-under-test spends.

Owning the gateway is what makes cost measurement reliable: the engine never
depends on a provider exposing usage, and it works identically across providers
and offline. `MockGateway` is deterministic so the demo and tests are
reproducible. A real adapter (Anthropic/OpenAI/UiPath AI Trust Layer) only has
to return token counts; the rest of the engine is unchanged.
"""

from __future__ import annotations

import os
import time
from dataclasses import dataclass

from .pricing import cost_usd


@dataclass(frozen=True)
class LLMResult:
    text: str
    model: str
    input_tokens: int
    output_tokens: int

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens

    @property
    def cost(self) -> float:
        return cost_usd(self.model, self.input_tokens, self.output_tokens)


class LLMGateway:
    """Interface. A real adapter implements `complete` against a provider and
    returns the true token usage.

    `produces_text` tells the patient whether the returned text is a real model
    answer to parse (real adapters) or a sentinel to ignore (the mock, which
    simulates extraction quality instead)."""

    produces_text: bool = False

    def complete(self, model: str, prompt: str, max_output_tokens: int = 400) -> LLMResult:
        raise NotImplementedError


def _retry(fn, attempts: int = 3, base_delay: float = 1.0):
    """Small backoff retry so a transient provider error (rate limit, blip)
    doesn't fail a whole regression run."""
    last = None
    for i in range(attempts):
        try:
            return fn()
        except Exception as e:  # noqa: BLE001 - provider SDKs raise varied types
            last = e
            if i < attempts - 1:
                time.sleep(base_delay * (2 ** i))
    raise last


# Per-model output verbosity multiplier — bigger models tend to emit more
# tokens for the same task, which is part of why "upgrading the model" can
# quietly inflate cost. Kept explicit so the simulation is auditable.
_VERBOSITY = {
    "claude-haiku-4-5": 1.0,
    "claude-sonnet-4-6": 1.25,
    "claude-opus-4-8": 1.7,
    "gpt-mini": 0.9,
    "gpt-large": 1.4,
}


class MockGateway(LLMGateway):
    """Deterministic, offline gateway. Token usage scales with prompt length
    and model verbosity — no network, no API key, fully reproducible."""

    def complete(self, model: str, prompt: str, max_output_tokens: int = 400) -> LLMResult:
        input_tokens = max(64, len(prompt) // 4)  # ~4 chars/token
        output_tokens = int(min(max_output_tokens, 170 * _VERBOSITY.get(model, 1.0)))
        return LLMResult(text="<<extracted-json>>", model=model,
                         input_tokens=input_tokens, output_tokens=output_tokens)


class AnthropicGateway(LLMGateway):
    """Real Claude gateway. Returns the model's text plus its true token usage,
    so cost is measured, never estimated. Lazy-imports the SDK so the offline
    engine has zero dependencies."""

    produces_text = True

    def __init__(self, api_key: str | None = None):
        try:
            import anthropic
        except ImportError as e:  # pragma: no cover
            raise ImportError("pip install anthropic to use AnthropicGateway") from e
        key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not key:
            raise RuntimeError("ANTHROPIC_API_KEY not set (put it in .env)")
        self._client = anthropic.Anthropic(api_key=key)

    def complete(self, model: str, prompt: str, max_output_tokens: int = 400) -> LLMResult:
        def call():
            return self._client.messages.create(
                model=model, max_tokens=max_output_tokens,
                messages=[{"role": "user", "content": prompt}])
        resp = _retry(call)
        text = "".join(getattr(b, "text", "") for b in resp.content
                       if getattr(b, "type", None) == "text")
        return LLMResult(text=text, model=model,
                         input_tokens=resp.usage.input_tokens,
                         output_tokens=resp.usage.output_tokens)


class OpenAIGateway(LLMGateway):
    """Real OpenAI gateway. Same contract as AnthropicGateway."""

    produces_text = True

    def __init__(self, api_key: str | None = None):
        try:
            import openai
        except ImportError as e:  # pragma: no cover
            raise ImportError("pip install openai to use OpenAIGateway") from e
        key = api_key or os.environ.get("OPENAI_API_KEY")
        if not key:
            raise RuntimeError("OPENAI_API_KEY not set (put it in .env)")
        self._client = openai.OpenAI(api_key=key)

    def complete(self, model: str, prompt: str, max_output_tokens: int = 400) -> LLMResult:
        def call():
            return self._client.chat.completions.create(
                model=model, max_tokens=max_output_tokens,
                messages=[{"role": "user", "content": prompt}])
        resp = _retry(call)
        text = resp.choices[0].message.content or ""
        return LLMResult(text=text, model=model,
                         input_tokens=resp.usage.prompt_tokens,
                         output_tokens=resp.usage.completion_tokens)
