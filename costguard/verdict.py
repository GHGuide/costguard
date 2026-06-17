"""The gate decision.

Three-valued so the system never bluffs on noisy data:
  PASS          — candidate is as cheap or cheaper per successful outcome.
  FAIL          — candidate is clearly more expensive per successful outcome
                  (its cost-per-success CI sits above the baseline's by more
                  than `cost_tolerance`).
  NEEDS_REVIEW  — the CIs overlap, or quality dropped: a human decides
                  (routed to UiPath Action Center in the platform integration).

Quality guard: a candidate that is cheaper but meaningfully *less* accurate is
never an automatic PASS — that is the "cheaper but dumber" trap, so it is sent
to review.
"""

from __future__ import annotations

from dataclasses import dataclass

from .stats import Summary


@dataclass(frozen=True)
class Verdict:
    verdict: str                 # "PASS" | "FAIL" | "NEEDS_REVIEW"
    cost_ratio: float            # candidate cost-per-success / baseline cost-per-success
    accuracy_delta: float        # candidate mean accuracy - baseline mean accuracy
    reasons: list[str]


def decide(baseline: Summary, candidate: Summary,
           cost_tolerance: float = 0.15, quality_tolerance: float = 0.02) -> Verdict:
    ratio = (candidate.cost_per_success / baseline.cost_per_success
             if baseline.cost_per_success not in (0, float("inf")) else float("inf"))
    acc_delta = candidate.mean_accuracy - baseline.mean_accuracy
    reasons: list[str] = []

    clearly_more_expensive = candidate.cps_ci_low > baseline.cps_ci_high * (1 + cost_tolerance)
    clearly_cheaper_or_equal = candidate.cps_ci_high <= baseline.cps_ci_low
    quality_regressed = acc_delta < -quality_tolerance

    if clearly_more_expensive:
        reasons.append(
            f"cost per successful invoice rose {ratio:.2f}x "
            f"(candidate CI ${candidate.cps_ci_low:.4f}-${candidate.cps_ci_high:.4f} vs "
            f"baseline ${baseline.cps_ci_low:.4f}-${baseline.cps_ci_high:.4f})")
        if acc_delta > quality_tolerance:
            reasons.append(f"quality improved only +{acc_delta*100:.1f}% accuracy — "
                           f"not worth the {ratio:.2f}x cost")
        return Verdict("FAIL", ratio, acc_delta, reasons)

    if quality_regressed:
        reasons.append(f"quality dropped {acc_delta*100:.1f}% accuracy — "
                       f"cheaper-but-worse, needs a human call")
        return Verdict("NEEDS_REVIEW", ratio, acc_delta, reasons)

    if clearly_cheaper_or_equal:
        reasons.append(f"cost per successful invoice held or improved ({ratio:.2f}x) "
                       f"with no quality loss")
        return Verdict("PASS", ratio, acc_delta, reasons)

    reasons.append("cost-per-success confidence intervals overlap — "
                   "difference is within noise; a human decides")
    return Verdict("NEEDS_REVIEW", ratio, acc_delta, reasons)
