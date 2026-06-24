"""Eval harness — meta-tests the gate itself.

A cost gate is only trustworthy if its verdicts are right. This runs a labelled
suite of regression scenarios (evals/scenarios.json) where the correct call is
economically obvious to a human, asks the gate to decide each, and scores it.

    python -m costguard.evals            # human table + accuracy
    python -m costguard.evals --json     # machine-readable, writes evals/result.json

The mock gateway is deterministic, so the score is reproducible. This is the
answer to "how do you know your gate is correct?" — 30 labelled cases, scored.
"""

from __future__ import annotations

import json
import os
import sys

from .dataset import make_invoices
from .gateway import MockGateway
from .patient import AgentConfig, InvoiceExtractionAgent
from .runner import run_config
from .stats import summarize
from .verdict import decide

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCENARIOS = os.path.join(HERE, "evals", "scenarios.json")


def _cfg(spec: dict, name: str) -> AgentConfig:
    return AgentConfig(name, spec["model"], spec.get("strategy", "simple"),
                       spec.get("accuracy", 0.92))


def run_eval(path: str = SCENARIOS, repeats: int = 20) -> dict:
    scenarios = json.load(open(path, encoding="utf-8"))["scenarios"]
    invoices = make_invoices(n=8, seed=7)
    agent = InvoiceExtractionAgent(MockGateway())
    rows, correct = [], 0
    by_class = {"PASS": [0, 0], "FAIL": [0, 0], "NEEDS_REVIEW": [0, 0]}  # [correct, total]
    for s in scenarios:
        base = summarize("b", run_config(agent, _cfg(s["baseline"], "b"), invoices, repeats=repeats, seed=1))
        cand = summarize("c", run_config(agent, _cfg(s["candidate"], "c"), invoices, repeats=repeats, seed=2))
        got = decide(base, cand).verdict
        ok = got == s["expected"]
        correct += ok
        by_class[s["expected"]][1] += 1
        by_class[s["expected"]][0] += ok
        rows.append({"id": s["id"], "name": s["name"], "expected": s["expected"],
                     "got": got, "ok": ok})
    return {"rows": rows, "correct": correct, "total": len(scenarios),
            "accuracy": round(correct / len(scenarios), 3),
            "by_class": {k: {"correct": v[0], "total": v[1]} for k, v in by_class.items()}}


def main() -> int:
    res = run_eval()
    if "--json" in sys.argv:
        os.makedirs(os.path.join(HERE, "evals"), exist_ok=True)
        with open(os.path.join(HERE, "evals", "result.json"), "w", encoding="utf-8") as fh:
            json.dump(res, fh, indent=2)
        print(json.dumps({k: res[k] for k in ("correct", "total", "accuracy", "by_class")}, indent=2))
        return 0
    print(f"\n  CostGuard gate eval — {res['total']} labelled scenarios\n")
    print(f"  {'id':<5}{'expected':<14}{'got':<14}{'':<3}name")
    print("  " + "-" * 72)
    for r in res["rows"]:
        print(f"  {r['id']:<5}{r['expected']:<14}{r['got']:<14}{'OK ' if r['ok'] else 'XX '}{r['name']}")
    print("  " + "-" * 72)
    print(f"  gate accuracy: {res['correct']}/{res['total']} = {res['accuracy']*100:.0f}%")
    for k, v in res["by_class"].items():
        print(f"    {k:<14} {v['correct']}/{v['total']}")
    return 0 if res["correct"] == res["total"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
