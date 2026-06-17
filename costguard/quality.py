"""Quality scoring for an extraction.

The gate measures cost *per successful business outcome*, so it needs an
objective definition of "successful". For invoice extraction that is field
accuracy vs ground truth. An invoice counts as successfully processed when at
least `threshold` of its required fields are correct (default 0.8 = 4 of 5),
mirroring a real straight-through-processing bar.

For a non-deterministic agent (e.g. a support agent) this scorer is swapped for
an LLM-as-judge; the rest of the engine is unchanged.
"""

from __future__ import annotations

from .patient import REQUIRED_FIELDS


def field_accuracy(extracted: dict, ground_truth: dict) -> float:
    correct = sum(1 for f in REQUIRED_FIELDS if extracted.get(f) == ground_truth.get(f))
    return correct / len(REQUIRED_FIELDS)


def is_success(extracted: dict, ground_truth: dict, threshold: float = 0.8) -> bool:
    return field_accuracy(extracted, ground_truth) >= threshold
