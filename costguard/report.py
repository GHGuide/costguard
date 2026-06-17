"""Assemble a machine-readable report.

This dict is what the UiPath integration registers as a Test Cloud result
(via the Test Manager API) and what the Maestro gate reads to decide
PASS -> promote, FAIL -> block, NEEDS_REVIEW -> Action Center.
"""

from __future__ import annotations

from .stats import Summary
from .verdict import Verdict


def _summary_dict(s: Summary) -> dict:
    return {
        "name": s.name,
        "n_runs": s.n_runs,
        "success_rate": round(s.success_rate, 4),
        "mean_accuracy": round(s.mean_accuracy, 4),
        "total_cost_usd": round(s.total_cost, 4),
        "cost_per_success_usd": round(s.cost_per_success, 6),
        "cost_per_success_ci": [round(s.cps_ci_low, 6), round(s.cps_ci_high, 6)],
        "mean_cost_per_run_usd": round(s.mean_cost_per_run, 6),
        "mean_tokens_per_run": round(s.mean_tokens_per_run, 1),
    }


def build_report(baseline: Summary, candidate: Summary, verdict: Verdict,
                 cost_per_outcome_unit: str = "invoice") -> dict:
    extra_cost_per_1k = (candidate.cost_per_success - baseline.cost_per_success) * 1000
    return {
        "gate": "costguard.cost_efficiency_regression",
        "outcome_unit": cost_per_outcome_unit,
        "verdict": verdict.verdict,
        "cost_ratio": round(verdict.cost_ratio, 3),
        "accuracy_delta": round(verdict.accuracy_delta, 4),
        "extra_cost_per_1000_outcomes_usd": round(extra_cost_per_1k, 2),
        "reasons": verdict.reasons,
        "baseline": _summary_dict(baseline),
        "candidate": _summary_dict(candidate),
    }
