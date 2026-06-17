"""Synthetic invoice scenario set with ground truth.

Stands in for a UiPath Document Understanding corpus so the engine runs offline.
Deterministic given a seed. Each item is {"id", "text", "ground_truth"} where
ground_truth holds the fields a correct extraction must recover.
"""

from __future__ import annotations

import random

_VENDORS = ["Globex GmbH", "Initech LLC", "Umbrella Corp", "Acme Industries",
            "Stark Supplies", "Wayne Logistics", "Soylent Foods", "Hooli Cloud"]
_CURRENCIES = ["USD", "EUR", "GBP"]


def _render(gt: dict) -> str:
    return (
        f"INVOICE\n"
        f"From: {gt['vendor']}\n"
        f"Invoice No: {gt['invoice_number']}\n"
        f"Due Date: {gt['due_date']}\n"
        f"Amount Due: {gt['currency']} {gt['total']:.2f}\n"
        f"Please remit payment by the due date. Thank you for your business."
    )


def make_invoices(n: int = 12, seed: int = 7) -> list[dict]:
    rng = random.Random(seed)
    out = []
    for i in range(n):
        gt = {
            "invoice_number": f"INV-{rng.randint(10000, 99999)}",
            "vendor": rng.choice(_VENDORS),
            "total": round(rng.uniform(100, 9000), 2),
            "currency": rng.choice(_CURRENCIES),
            "due_date": f"2026-{rng.randint(1, 12):02d}-{rng.randint(1, 28):02d}",
        }
        out.append({"id": f"doc-{i:03d}", "text": _render(gt), "ground_truth": gt})
    return out
