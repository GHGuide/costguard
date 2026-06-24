"""Run the CostGuard gate on REAL models through the UiPath AI Trust Layer LLM
Gateway — real token usage, real cost-per-correct-invoice, no external API key.

    export UIPATH_ACCESS_TOKEN=...   # a bearer token (see costguard.uipath.auth.get_token)
    export UIPATH_URL=https://staging.uipath.com/<org>/<tenant>
    uv run --with uipath python -m costguard.uipath.run_live

Writes docs/live-uipath-result.json (real evidence for the README / submission).
"""

from __future__ import annotations

import json

from ..cli import _print_human
from ..dataset import make_invoices
from ..gateway import UiPathLLMGateway
from ..patient import AgentConfig, InvoiceExtractionAgent
from ..report import build_report
from ..runner import run_config
from ..stats import summarize
from ..verdict import decide


def main() -> int:
    invoices = make_invoices(n=5, seed=7)
    agent = InvoiceExtractionAgent(UiPathLLMGateway())

    baseline = AgentConfig("baseline · gpt-4.1-mini · simple", "gpt-4.1-mini-2025-04-14", "simple")
    candidate = AgentConfig("candidate · gpt-4o · verify", "gpt-4o-2024-08-06", "verify")

    print("Running on real UiPath LLM Gateway models — this makes live API calls ...")
    b = summarize(baseline.name, run_config(agent, baseline, invoices, repeats=2, seed=1))
    c = summarize(candidate.name, run_config(agent, candidate, invoices, repeats=2, seed=2))
    report = build_report(b, c, decide(b, c))

    # second agent: root-cause the cost move, explained by a real model on UiPath
    from ..explainer import attribute, explain
    if report["verdict"] != "PASS":
        report["attribution"] = attribute(baseline, candidate, report)
        report["explanation"] = explain(report["attribution"], gateway=agent.gw)

    _print_human(report)
    if report.get("explanation"):
        print("\n  Cost Explainer (2nd agent, on UiPath):\n  " + report["explanation"])
    with open("docs/live-uipath-result.json", "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2)
    print("\nsaved docs/live-uipath-result.json  (real models, real tokens, via UiPath)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
