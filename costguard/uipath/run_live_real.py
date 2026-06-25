"""Gate the agent on a REALISTIC invoice corpus, live on the UiPath LLM Gateway.

Same gate as `run_live`, but the inputs are varied real-world invoice layouts
(`dataset_real`) instead of templated synthetic ones — so the extraction accuracy
is genuinely measured on messy data (label variants, $/€/£, OCR noise, multi-line,
discounts/VAT), not a formality. This is the honest answer to "but the patient is
a mock": real models, real tokens, real cost, real measured accuracy.

    export UIPATH_ACCESS_TOKEN=...    # see costguard.uipath.auth.get_token
    export UIPATH_URL=https://staging.uipath.com/<org>/<tenant>
    uv run --with uipath python -m costguard.uipath.run_live_real

Writes docs/live-real-result.json.
"""

from __future__ import annotations

import json

from ..cli import _print_human
from ..dataset_real import make_realistic_invoices
from ..gateway import UiPathLLMGateway
from ..patient import AgentConfig, InvoiceExtractionAgent
from ..report import build_report
from ..runner import run_config
from ..stats import summarize
from ..verdict import decide


def main() -> int:
    invoices = make_realistic_invoices()
    agent = InvoiceExtractionAgent(UiPathLLMGateway())

    baseline = AgentConfig("baseline · gpt-4.1-mini · simple", "gpt-4.1-mini-2025-04-14", "simple")
    candidate = AgentConfig("candidate · gpt-4o · verify", "gpt-4o-2024-08-06", "verify")

    print(f"Gating on {len(invoices)} realistic invoices via the UiPath LLM Gateway — "
          "real models, real extraction, measured accuracy ...\n")
    b = summarize(baseline.name, run_config(agent, baseline, invoices, repeats=2, seed=1))
    c = summarize(candidate.name, run_config(agent, candidate, invoices, repeats=2, seed=2))
    report = build_report(b, c, decide(b, c))

    from ..explainer import attribute, explain
    if report["verdict"] != "PASS":
        report["attribution"] = attribute(baseline, candidate, report)
        report["explanation"] = explain(report["attribution"], gateway=agent.gw)

    _print_human(report)
    print(f"\n  MEASURED accuracy on realistic invoices (not simulated):")
    print(f"    baseline  {baseline.model:24}  {b.mean_accuracy*100:5.1f}%  correct-field rate")
    print(f"    candidate {candidate.model:24}  {c.mean_accuracy*100:5.1f}%  correct-field rate")
    if report.get("explanation"):
        print("\n  Cost Explainer (2nd agent, on UiPath):\n  " + report["explanation"])

    report["dataset"] = "realistic (dataset_real, 12 varied real-world layouts)"
    with open("docs/live-real-result.json", "w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2)
    print("\nsaved docs/live-real-result.json  (real models, realistic invoices, measured accuracy)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
