"""Model pricing table: tokens -> USD.

Rates are USD per 1,000,000 tokens (input, output). Illustrative 2026 list
prices; in the UiPath integration these are refreshed from a live pricing
API Workflow so the gate always costs against current rates.
"""

PRICING = {
    "claude-haiku-4-5":   {"input": 1.00,  "output": 5.00},
    "claude-sonnet-4-6":  {"input": 3.00,  "output": 15.00},
    "claude-opus-4-8":    {"input": 15.00, "output": 75.00},
    "gpt-mini":           {"input": 0.50,  "output": 1.50},
    "gpt-large":          {"input": 10.00, "output": 30.00},
    "gpt-4o-mini":        {"input": 0.15,  "output": 0.60},
    "gpt-4o":             {"input": 2.50,  "output": 10.00},
}


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
