"""Ledger / savings-math tests. Run: python tests/test_ledger.py (or pytest)."""

from __future__ import annotations

import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from costguard.dashboard import _mini_report, render, seed_demo
from costguard.ledger import Ledger


def test_avoided_savings_on_fail():
    led = Ledger()
    led.record(_mini_report("FAIL", 0.010, 0.080, +0.01), "a", "v2", "v1", 10_000, ts="t1")
    e = led.latest("a")
    assert e.savings_kind == "avoided"
    assert e.savings_usd == round((0.080 - 0.010) * 10_000, 2)  # 700.0


def test_realized_savings_on_pass_cheaper():
    led = Ledger()
    led.record(_mini_report("PASS", 0.010, 0.006, -0.001), "a", "v2", "v1", 10_000, ts="t1")
    e = led.latest("a")
    assert e.savings_kind == "realized"
    assert e.savings_usd == round((0.010 - 0.006) * 10_000, 2)  # 40.0


def test_needs_review_is_pending_no_savings():
    led = Ledger()
    led.record(_mini_report("NEEDS_REVIEW", 0.010, 0.006, -0.05), "a", "v2", "v1", 10_000, ts="t1")
    assert led.latest("a").savings_kind == "pending"
    assert led.latest("a").savings_usd == 0.0


def test_current_cost_reflects_adoption():
    led = Ledger()
    # blocked candidate never ships -> still on baseline
    led.record(_mini_report("FAIL", 0.010, 0.080, +0.01), "a", "v2", "v1", 10_000, ts="t1")
    assert led.current_cost_per_outcome("a") == 0.010
    # then a cheaper PASS is adopted -> current cost drops to candidate
    led.record(_mini_report("PASS", 0.010, 0.007, 0.0), "a", "v3", "v1", 10_000, ts="t2")
    assert led.current_cost_per_outcome("a") == 0.007


def test_totals_sum():
    led = seed_demo()
    t = led.totals()
    assert t["total_monthly_usd"] == round(t["avoided_monthly_usd"] + t["realized_monthly_usd"], 2)
    assert t["total_annual_usd"] == round(t["total_monthly_usd"] * 12, 2)
    assert t["regressions_blocked"] == 1


def test_save_load_roundtrip():
    led = seed_demo()
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "ledger.json")
        led.save(p)
        back = Ledger.load(p)
    assert len(back.events) == len(led.events)
    assert back.totals() == led.totals()


def test_render_runs():
    assert "SAVINGS LEDGER" in render(seed_demo())


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    failed = 0
    for fn in fns:
        try:
            fn()
            print(f"PASS {fn.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"FAIL {fn.__name__}: {e}")
    print(f"\n{len(fns) - failed}/{len(fns)} passed")
    raise SystemExit(1 if failed else 0)
