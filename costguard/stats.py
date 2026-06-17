"""Statistics over run records.

The headline metric is **cost per successful outcome** = total cost / number of
successfully-processed invoices. A bootstrap confidence interval over the run
records turns a noisy ratio into a band, so the gate compares bands, not single
numbers — the right way to reason about a non-deterministic system.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from .runner import RunRecord


def cost_per_success(records: list[RunRecord]) -> float:
    successes = sum(1 for r in records if r.success)
    total_cost = sum(r.cost for r in records)
    if successes == 0:
        return float("inf")
    return total_cost / successes


def _bootstrap_ci(records: list[RunRecord], n: int = 2000, alpha: float = 0.05,
                  seed: int = 1) -> tuple[float, float]:
    rng = random.Random(seed)
    k = len(records)
    samples = []
    for _ in range(n):
        resample = [records[rng.randrange(k)] for _ in range(k)]
        samples.append(cost_per_success(resample))
    samples = [s for s in samples if s != float("inf")]
    if not samples:
        return float("inf"), float("inf")
    samples.sort()
    lo = samples[int(alpha / 2 * len(samples))]
    hi = samples[min(len(samples) - 1, int((1 - alpha / 2) * len(samples)))]
    return lo, hi


@dataclass(frozen=True)
class Summary:
    name: str
    n_runs: int
    successes: int
    success_rate: float
    total_cost: float
    cost_per_success: float
    cps_ci_low: float
    cps_ci_high: float
    mean_accuracy: float
    mean_cost_per_run: float
    mean_tokens_per_run: float


def summarize(name: str, records: list[RunRecord]) -> Summary:
    n = len(records)
    successes = sum(1 for r in records if r.success)
    lo, hi = _bootstrap_ci(records)
    return Summary(
        name=name,
        n_runs=n,
        successes=successes,
        success_rate=successes / n if n else 0.0,
        total_cost=sum(r.cost for r in records),
        cost_per_success=cost_per_success(records),
        cps_ci_low=lo,
        cps_ci_high=hi,
        mean_accuracy=sum(r.accuracy for r in records) / n if n else 0.0,
        mean_cost_per_run=sum(r.cost for r in records) / n if n else 0.0,
        mean_tokens_per_run=sum(r.tokens for r in records) / n if n else 0.0,
    )
