"""Stress test — fuzz the gate with random agent configs and assert invariants
never break (no crash, valid verdict, sane cost bands). Run: python tests/test_stress.py
"""

from __future__ import annotations

import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from costguard.dataset import make_invoices
from costguard.gateway import MockGateway
from costguard.patient import AgentConfig, InvoiceExtractionAgent
from costguard.report import build_report
from costguard.runner import run_config
from costguard.stats import summarize
from costguard.verdict import decide

_MODELS = ["claude-haiku-4-5", "claude-sonnet-4-6", "claude-opus-4-8",
           "gpt-4o-mini", "gpt-4o", "gpt-4.1-mini"]


def test_fuzz_150_random_configs_hold_invariants():
    invoices = make_invoices(n=6, seed=7)
    agent = InvoiceExtractionAgent(MockGateway())
    rng = random.Random(0)
    for i in range(150):
        c1 = AgentConfig("b", rng.choice(_MODELS), rng.choice(["simple", "verify"]), rng.uniform(0, 1))
        c2 = AgentConfig("c", rng.choice(_MODELS), rng.choice(["simple", "verify"]), rng.uniform(0, 1))
        b = summarize("b", run_config(agent, c1, invoices, repeats=rng.choice([1, 2, 10]), seed=i))
        c = summarize("c", run_config(agent, c2, invoices, repeats=rng.choice([1, 2, 10]), seed=i + 7))
        v = decide(b, c)
        r = build_report(b, c, v)
        assert v.verdict in ("PASS", "FAIL", "NEEDS_REVIEW")
        assert r["cost_ratio"] >= 0 or math.isinf(r["cost_ratio"])
        assert b.cps_ci_low <= b.cps_ci_high or math.isinf(b.cps_ci_high)
        assert 0.0 <= b.success_rate <= 1.0 and 0.0 <= c.success_rate <= 1.0


def test_all_fail_gives_infinite_cost_per_success_not_crash():
    # per_field_accuracy 0 -> no invoice ever fully correct -> cps = inf, no divide-by-zero
    invoices = make_invoices(n=4, seed=7)
    agent = InvoiceExtractionAgent(MockGateway())
    s = summarize("z", run_config(agent, AgentConfig("z", "claude-haiku-4-5", "simple", 0.0),
                                  invoices, repeats=5, seed=1))
    assert s.cost_per_success == float("inf")


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    failed = 0
    for fn in fns:
        try:
            fn(); print(f"PASS {fn.__name__}")
        except AssertionError as e:
            failed += 1; print(f"FAIL {fn.__name__}: {e}")
    print(f"\n{len(fns) - failed}/{len(fns)} passed")
    raise SystemExit(1 if failed else 0)
