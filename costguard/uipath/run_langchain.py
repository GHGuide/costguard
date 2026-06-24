"""Gate an EXTERNAL LangChain agent (running on UiPath models) with CostGuard.

    export UIPATH_ACCESS_TOKEN=...   UIPATH_URL=https://staging.uipath.com/<org>/<tenant>
    uv run --with 'langchain-core,uipath' python -m costguard.uipath.run_langchain

Writes docs/live-langchain-result.json — proof CostGuard tests a third-party
framework's agent, governed by UiPath.
"""

from __future__ import annotations

import json

from ..cli import _print_human
from ..dataset import make_invoices
from ..patient import AgentConfig
from ..report import build_report
from ..runner import run_config
from ..stats import summarize
from ..verdict import decide
from .langchain_patient import LangChainInvoiceAgent


def main() -> int:
    invoices = make_invoices(n=5, seed=7)
    agent = LangChainInvoiceAgent()

    baseline = AgentConfig("LangChain · gpt-4.1-mini · simple", "gpt-4.1-mini-2025-04-14", "simple")
    candidate = AgentConfig("LangChain · gpt-4o · verify", "gpt-4o-2024-08-06", "verify")

    print("Gating an external LangChain agent on real UiPath models — live API calls ...")
    b = summarize(baseline.name, run_config(agent, baseline, invoices, repeats=2, seed=1))
    c = summarize(candidate.name, run_config(agent, candidate, invoices, repeats=2, seed=2))
    report = build_report(b, c, decide(b, c))

    _print_human(report)
    with open("docs/live-langchain-result.json", "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2)
    print("\nsaved docs/live-langchain-result.json  (external LangChain agent, governed by UiPath)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
