"""CostGuard — an agentic cost & efficiency regression gate for AI agents.

Catches when a change to an AI agent (prompt / model / tool) makes it silently
more expensive *per successfully-completed business outcome*, and blocks
promotion before it ships. Built for UiPath AgentHack 2026, Track 3 (Test Cloud).

The engine is provider- and platform-agnostic and runs fully offline with a
deterministic MockGateway. Swap in a real LLM adapter and the UiPath integration
without touching the stats/verdict core.
"""

from .pricing import cost_usd, resolve, PRICING
from .gateway import (LLMGateway, MockGateway, AnthropicGateway, OpenAIGateway,
                      UiPathLLMGateway, LLMResult)
from .patient import InvoiceExtractionAgent, AgentConfig, REQUIRED_FIELDS
from .runner import run_config, RunRecord
from .stats import summarize, Summary
from .verdict import decide, Verdict
from .ledger import Ledger, GateEvent

__all__ = [
    "cost_usd", "resolve", "PRICING",
    "LLMGateway", "MockGateway", "AnthropicGateway", "OpenAIGateway",
    "UiPathLLMGateway", "LLMResult",
    "InvoiceExtractionAgent", "AgentConfig", "REQUIRED_FIELDS",
    "run_config", "RunRecord",
    "summarize", "Summary",
    "decide", "Verdict",
    "Ledger", "GateEvent",
]
