"""CostGuard coded-agent entrypoint (UiPath Python SDK).

This is the function the UiPath runtime invokes (and that `uip run` calls
locally). It takes the Maestro INPUT_SCHEMA, runs the cost/efficiency gate,
records the savings ledger, registers the Test Cloud result, builds the HITL
task when needed, and returns the OUTPUT_SCHEMA for Maestro to branch on.

Run offline:
    python -m costguard.uipath.coded_agent            # built-in demo input
    python -m costguard.uipath.coded_agent --input in.json
"""

from __future__ import annotations

import json
import os
import sys

from ..dataset import make_invoices
from ..gateway import AnthropicGateway, MockGateway, OpenAIGateway
from ..ledger import Ledger
from ..patient import AgentConfig, InvoiceExtractionAgent
from ..report import build_report
from ..runner import run_config
from ..stats import summarize
from ..verdict import decide
from .action_center import ActionCenterClient
from .config import load_config
from .maestro_contract import decide_action
from .test_manager import TestManagerClient

LEDGER_PATH = "data/ledger.json"

DEMO_INPUT = {
    "agent": "invoice-extractor", "outcome_unit": "invoice", "monthly_outcomes": 50_000,
    "provider": "mock",
    "baseline": {"name": "v1", "model": "claude-haiku-4-5", "strategy": "simple",
                 "per_field_accuracy": 0.92},
    "candidate": {"name": "v2", "model": "claude-sonnet-4-6", "strategy": "verify",
                  "per_field_accuracy": 0.94},
    "n_invoices": 12, "repeats": 20,
    "cost_tolerance": 0.15, "quality_tolerance": 0.02, "dry_run": True,
}


def _gateway(provider: str):
    if provider == "anthropic":
        return AnthropicGateway()
    if provider == "openai":
        return OpenAIGateway()
    return MockGateway()


def _config(d: dict) -> AgentConfig:
    return AgentConfig(name=d["name"], model=d["model"],
                       strategy=d.get("strategy", "simple"),
                       per_field_accuracy=d.get("per_field_accuracy", 0.92))


def run_gate(inp: dict) -> dict:
    dry_run = inp.get("dry_run", True)
    invoices = make_invoices(n=inp.get("n_invoices", 12), seed=7)
    agent = InvoiceExtractionAgent(_gateway(inp.get("provider", "mock")))
    base_cfg, cand_cfg = _config(inp["baseline"]), _config(inp["candidate"])

    base = summarize(base_cfg.name, run_config(agent, base_cfg, invoices,
                                               repeats=inp.get("repeats", 20), seed=1))
    cand = summarize(cand_cfg.name, run_config(agent, cand_cfg, invoices,
                                               repeats=inp.get("repeats", 20), seed=2))
    verdict = decide(base, cand, cost_tolerance=inp.get("cost_tolerance", 0.15),
                     quality_tolerance=inp.get("quality_tolerance", 0.02))
    report = build_report(base, cand, verdict, cost_per_outcome_unit=inp.get("outcome_unit", "invoice"))

    # record to the savings ledger (drives the dashboard)
    ledger = Ledger.load(LEDGER_PATH) if os.path.exists(LEDGER_PATH) else Ledger()
    event = ledger.record(report, agent=inp.get("agent", "agent"), version=cand_cfg.name,
                          baseline_version=base_cfg.name,
                          monthly_outcomes=inp.get("monthly_outcomes", 0))
    os.makedirs(os.path.dirname(LEDGER_PATH) or ".", exist_ok=True)
    ledger.save(LEDGER_PATH)

    tm = TestManagerClient(load_config(), dry_run=dry_run).register(report)
    hitl = ActionCenterClient(load_config(), dry_run=dry_run).create_task(report)

    return {
        "verdict": report["verdict"],
        "maestro_action": decide_action(report["verdict"]),
        "report": report,
        "test_manager": tm,
        "hitl_task": hitl,
        "ledger_event": event.__dict__,
    }


# Alias the UiPath runtime can target as the agent entrypoint.
entrypoint = run_gate


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    inp = dict(DEMO_INPUT)
    if "--input" in argv:
        with open(argv[argv.index("--input") + 1], encoding="utf-8") as fh:
            inp = json.load(fh)
    result = run_gate(inp)
    print(json.dumps(result, indent=2))
    print(f"\n→ verdict={result['verdict']}  maestro_action={result['maestro_action']}  "
          f"test_manager={result['test_manager'].get('status')}  "
          f"hitl={'created' if result['hitl_task'] else 'none'}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
