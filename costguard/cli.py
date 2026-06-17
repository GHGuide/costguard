"""CostGuard demo CLI.

    python -m costguard.cli

Runs a baseline agent vs a "looks better" candidate agent over the invoice
scenario set, computes cost-per-successful-invoice with confidence intervals,
and prints the gate verdict — the whole thesis, offline, in one command.

The default scenario is the hero demo: the candidate upgrades the model and
adds a "double-check" pass. Accuracy ticks up a hair; cost-per-successful-
invoice explodes. CostGuard blocks it.
"""

from __future__ import annotations

import json
import sys

from .dataset import make_invoices
from .gateway import MockGateway
from .patient import AgentConfig, InvoiceExtractionAgent
from .report import build_report
from .runner import run_config
from .stats import summarize
from .verdict import decide

BASELINE = AgentConfig(name="invoice-extractor v1", model="claude-haiku-4-5",
                       strategy="simple", per_field_accuracy=0.92)
CANDIDATE = AgentConfig(name="invoice-extractor v2", model="claude-sonnet-4-6",
                        strategy="verify", per_field_accuracy=0.94)


def _fmt_usd(x: float) -> str:
    return f"${x:,.4f}" if x < 1 else f"${x:,.2f}"


def run_demo(repeats: int = 20) -> dict:
    invoices = make_invoices(n=12, seed=7)
    agent = InvoiceExtractionAgent(MockGateway())

    base_records = run_config(agent, BASELINE, invoices, repeats=repeats, seed=1)
    cand_records = run_config(agent, CANDIDATE, invoices, repeats=repeats, seed=2)

    base = summarize(BASELINE.name, base_records)
    cand = summarize(CANDIDATE.name, cand_records)
    verdict = decide(base, cand)
    return build_report(base, cand, verdict)


def _print_human(report: dict) -> None:
    b, c = report["baseline"], report["candidate"]
    icon = {"PASS": "PASS  ✅", "FAIL": "FAIL  ⛔", "NEEDS_REVIEW": "NEEDS REVIEW  🟡"}[report["verdict"]]
    bar = "─" * 64
    print(bar)
    print("  CostGuard — cost & efficiency regression gate")
    print(f"  outcome unit: 1 correctly-processed {report['outcome_unit']}")
    print(bar)
    row = "  {:<20}{:>26}{:>26}"
    bn, cn = b["name"][:25], c["name"][:25]
    print(row.format("", bn, cn))
    print(row.format("success rate", f"{b['success_rate']*100:.1f}%", f"{c['success_rate']*100:.1f}%"))
    print(row.format("mean field accuracy", f"{b['mean_accuracy']*100:.1f}%", f"{c['mean_accuracy']*100:.1f}%"))
    print(row.format("mean cost / run", _fmt_usd(b["mean_cost_per_run_usd"]), _fmt_usd(c["mean_cost_per_run_usd"])))
    print(row.format("COST / SUCCESS", _fmt_usd(b["cost_per_success_usd"]), _fmt_usd(c["cost_per_success_usd"])))
    print(row.format("  95% CI low", _fmt_usd(b["cost_per_success_ci"][0]), _fmt_usd(c["cost_per_success_ci"][0])))
    print(row.format("  95% CI high", _fmt_usd(b["cost_per_success_ci"][1]), _fmt_usd(c["cost_per_success_ci"][1])))
    print(bar)
    print(f"  VERDICT: {icon}")
    print(f"  cost per successful {report['outcome_unit']}: {report['cost_ratio']:.2f}x baseline")
    print(f"  quality delta: {report['accuracy_delta']*100:+.1f}% accuracy")
    print(f"  extra cost per 1,000 {report['outcome_unit']}s: "
          f"${report['extra_cost_per_1000_outcomes_usd']:,.2f}")
    for r in report["reasons"]:
        print(f"   • {r}")
    print(bar)


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    as_json = "--json" in argv
    report = run_demo()
    if as_json:
        print(json.dumps(report, indent=2))
    else:
        _print_human(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
