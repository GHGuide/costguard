"""The agent-under-test ("patient").

In production this is a UiPath Document Understanding + Agent Builder invoice
extraction agent. Here it is simulated so CostGuard runs fully offline: it makes
real (mock) gateway calls for honest token/cost accounting, and simulates
extraction accuracy as a function of model capability and strategy.

CostGuard treats the patient as a black box: give it an input + a config, read
back the extracted fields and the cost. Any agent that honours this contract can
be tested — including an external LangChain / CrewAI agent.
"""

from __future__ import annotations

import json
import random
import re
from dataclasses import dataclass

from .gateway import LLMGateway

REQUIRED_FIELDS = ["invoice_number", "vendor", "total", "currency", "due_date"]


@dataclass(frozen=True)
class AgentConfig:
    """A version of the agent. Changing any of these is exactly the kind of
    edit CostGuard regression-tests."""
    name: str
    model: str
    strategy: str = "simple"        # "simple" = one call; "verify" = adds a re-check call
    per_field_accuracy: float = 0.92  # simulated capability (real agent: measured, not set)


def _corrupt(value, rng: random.Random):
    if isinstance(value, str):
        return value[:-1] + "?" if value else "?"
    if isinstance(value, float):
        return round(value * rng.uniform(1.05, 1.4), 2)  # wrong amount
    return None


class InvoiceExtractionAgent:
    def __init__(self, gateway: LLMGateway):
        self.gw = gateway

    def _prompt(self, text: str, config: AgentConfig) -> str:
        base = ("Extract these fields from the invoice and return ONLY a JSON object with keys "
                "invoice_number, vendor, total, currency, due_date. "
                "`total` must be a number, `due_date` as YYYY-MM-DD. Document:\n\n" + text)
        if config.strategy == "verify":
            base += "\n\nReason about each field carefully before producing the JSON."
        return base

    def run(self, invoice: dict, config: AgentConfig, rng: random.Random) -> dict:
        prompt = self._prompt(invoice["text"], config)
        calls = [self.gw.complete(config.model, prompt)]
        if config.strategy == "verify":
            calls.append(self.gw.complete(
                config.model, prompt + "\n\nDouble-check every field and re-extract. Output only JSON."))

        if getattr(self.gw, "produces_text", False):
            extracted = self._parse(calls[-1].text, invoice["ground_truth"])  # real model output
        else:
            extracted = self._simulate(invoice["ground_truth"], config, rng)  # offline mock

        return {
            "extracted": extracted,
            "cost": sum(c.cost for c in calls),
            "tokens": sum(c.total_tokens for c in calls),
            "calls": len(calls),
        }

    def _simulate(self, gt: dict, config: AgentConfig, rng: random.Random) -> dict:
        acc = config.per_field_accuracy
        if config.strategy == "verify":
            acc = min(0.995, acc + 0.03)  # the verify pass nudges accuracy up a little
        return {f: (gt[f] if rng.random() < acc else _corrupt(gt[f], rng)) for f in REQUIRED_FIELDS}

    def _parse(self, text: str, gt: dict) -> dict:
        """Pull the JSON object out of a real model response and normalize field
        types so the comparison to ground truth is fair. Unparseable -> empty
        fields (which simply scores as a miss)."""
        match = re.search(r"\{.*\}", text or "", re.DOTALL)
        data = {}
        if match:
            try:
                data = json.loads(match.group(0))
            except (ValueError, TypeError):
                data = {}
        out = {}
        for f in REQUIRED_FIELDS:
            v = data.get(f)
            if f == "total":
                try:
                    v = round(float(str(v).replace(",", "").replace("$", "").strip()), 2)
                except (ValueError, TypeError):
                    v = None
            elif isinstance(v, str):
                v = v.strip()
            out[f] = v
        return out
