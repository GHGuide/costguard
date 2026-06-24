"""Model pricing table: tokens -> USD.

Rates are USD per 1,000,000 tokens (input, output). Illustrative 2026 list
prices; they are refreshable at runtime (see `refresh_pricing`) from a live
source, so the gate always costs against current rates. In the UiPath
integration a pricing API Workflow writes those current rates.
"""

from __future__ import annotations

import json
import os

PRICING = {
    "claude-haiku-4-5":   {"input": 1.00,  "output": 5.00},
    "claude-sonnet-4-6":  {"input": 3.00,  "output": 15.00},
    "claude-opus-4-8":    {"input": 15.00, "output": 75.00},
    "gpt-mini":           {"input": 0.50,  "output": 1.50},
    "gpt-large":          {"input": 10.00, "output": 30.00},
    "gpt-4o-mini":        {"input": 0.15,  "output": 0.60},
    "gpt-4o":             {"input": 2.50,  "output": 10.00},
    "gpt-4.1-mini":       {"input": 0.40,  "output": 1.60},
    "gpt-4.1-nano":       {"input": 0.10,  "output": 0.40},
    "gpt-4.1":            {"input": 2.00,  "output": 8.00},
}


def refresh_pricing() -> int:
    """Merge live pricing overrides into PRICING and return how many rows changed.

    Source (first that exists wins): a JSON file at ``COSTGUARD_PRICING_FILE`` or
    inline JSON in ``COSTGUARD_PRICING_JSON``, shaped like PRICING
    (``{"model": {"input": 1.0, "output": 5.0}}``). In the platform a pricing API
    Workflow writes that file; offline with no override this is a safe no-op, so the
    gate always costs against current rates without a code change."""
    raw = None
    path = os.environ.get("COSTGUARD_PRICING_FILE")
    if path and os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            raw = fh.read()
    raw = raw or os.environ.get("COSTGUARD_PRICING_JSON")
    if not raw:
        return 0
    try:
        data = json.loads(raw)
    except ValueError:
        return 0
    changed = 0
    for model, row in (data or {}).items():
        if isinstance(row, dict) and "input" in row and "output" in row:
            PRICING[model] = {"input": float(row["input"]), "output": float(row["output"])}
            changed += 1
    return changed


def resolve(model: str) -> dict:
    """Find the pricing row for a model id. Exact match first, then a prefix
    match so dated ids (e.g. claude-haiku-4-5-20251001) resolve to their family.
    Raises on a miss so a silent pricing gap can never hide a cost regression."""
    if model in PRICING:
        return PRICING[model]
    for key, row in PRICING.items():
        if model.startswith(key) or key.startswith(model):
            return row
    raise KeyError(f"No pricing for model {model!r}; add it to PRICING.")


def cost_usd(model: str, input_tokens: int, output_tokens: int) -> float:
    """Dollar cost of one LLM call."""
    p = resolve(model)
    return input_tokens / 1_000_000 * p["input"] + output_tokens / 1_000_000 * p["output"]


# Apply any live pricing override at import (no-op offline with no override set).
refresh_pricing()
