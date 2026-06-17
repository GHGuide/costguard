"""N-run harness.

Because agents are non-deterministic, a single run lies. The runner executes an
agent config over the whole scenario set, `repeats` times, and records the cost
and the success of every individual run. Those per-run records are the unit the
statistics resample over.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from .patient import AgentConfig, InvoiceExtractionAgent
from .quality import field_accuracy, is_success


@dataclass(frozen=True)
class RunRecord:
    doc_id: str
    cost: float
    tokens: int
    success: bool
    accuracy: float


def run_config(agent: InvoiceExtractionAgent, config: AgentConfig, invoices: list[dict],
               repeats: int = 20, seed: int = 0, success_threshold: float = 0.8) -> list[RunRecord]:
    rng = random.Random(seed)
    records: list[RunRecord] = []
    for _ in range(repeats):
        for inv in invoices:
            res = agent.run(inv, config, rng)
            records.append(RunRecord(
                doc_id=inv["id"],
                cost=res["cost"],
                tokens=res["tokens"],
                success=is_success(res["extracted"], inv["ground_truth"], success_threshold),
                accuracy=field_accuracy(res["extracted"], inv["ground_truth"]),
            ))
    return records
