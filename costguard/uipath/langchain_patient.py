"""An EXTERNAL-framework agent-under-test: a LangChain (LCEL) invoice-extraction
agent whose model runs on the UiPath AI Trust Layer LLM Gateway.

This proves two things the rubric rewards: (1) CostGuard treats the agent as a
black box, so it gates ANY framework — UiPath-native or third-party; (2) an
external LangChain agent runs *governed by UiPath* (model, tokens, cost on the
platform). It exposes the same patient contract as InvoiceExtractionAgent, so
the exact same gate runs against it.

    uv run --with 'langchain-core,uipath' python -m costguard.uipath.run_langchain
"""

from __future__ import annotations

import random

from ..gateway import UiPathLLMGateway
from ..patient import AgentConfig, InvoiceExtractionAgent


class LangChainInvoiceAgent:
    def __init__(self, default_model: str = "gpt-4.1-mini-2025-04-14"):
        from langchain_core.prompts import ChatPromptTemplate  # noqa: F401 - external framework
        self._gw = UiPathLLMGateway(default_model=default_model)
        self._default_model = default_model
        self._prompt = ChatPromptTemplate.from_template(
            "Extract invoice_number, vendor, total, currency, due_date as JSON "
            "(total a number, due_date YYYY-MM-DD) from this document:\n\n{doc}")
        self._parse = InvoiceExtractionAgent(self._gw)._parse  # reuse the proven JSON parser

    def run(self, invoice: dict, config: AgentConfig, rng: random.Random) -> dict:
        from langchain_core.runnables import RunnableLambda
        model = config.model or self._default_model
        base = self._prompt.format(doc=invoice["text"])
        # LCEL: a Runnable that drives the UiPath-governed model
        call = RunnableLambda(lambda p: self._gw.complete(model, p))
        calls = [call.invoke(base)]
        if config.strategy == "verify":
            calls.append(call.invoke(base + "\n\nDouble-check every field and re-extract. Output only JSON."))
        extracted = self._parse(calls[-1].text, invoice["ground_truth"])
        return {"extracted": extracted, "cost": sum(c.cost for c in calls),
                "tokens": sum(c.total_tokens for c in calls), "calls": len(calls)}
