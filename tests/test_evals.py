"""The gate must keep scoring 100% on the labelled eval suite."""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from costguard.evals import run_eval


def test_gate_scores_100pct_on_labelled_scenarios():
    res = run_eval()
    assert res["total"] >= 30, "eval suite should have at least 30 labelled scenarios"
    assert res["correct"] == res["total"], (
        f"gate mis-decided {res['total'] - res['correct']} scenario(s): "
        + ", ".join(r["id"] for r in res["rows"] if not r["ok"]))


def test_eval_covers_all_three_verdicts():
    res = run_eval()
    for verdict in ("PASS", "FAIL", "NEEDS_REVIEW"):
        assert res["by_class"][verdict]["total"] >= 3, f"too few {verdict} scenarios"


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
