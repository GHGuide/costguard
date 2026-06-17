"""The contract between the Maestro gate process and the CostGuard coded agent.

Maestro orchestrates: it calls the coded agent with INPUT_SCHEMA, receives
OUTPUT_SCHEMA back, then branches on `maestro_action`:
    promote   -> PASS: let the new agent version ship
    block     -> FAIL: stop the promotion
    escalate  -> NEEDS_REVIEW: open an Action Center task for a human
"""

from __future__ import annotations

# verdict -> what Maestro should do next
DECISION = {"PASS": "promote", "FAIL": "block", "NEEDS_REVIEW": "escalate"}


def decide_action(verdict: str) -> str:
    if verdict not in DECISION:
        raise ValueError(f"unknown verdict {verdict!r}")
    return DECISION[verdict]


# What Maestro sends to the coded agent.
INPUT_SCHEMA = {
    "agent": "str — logical name of the agent under test",
    "outcome_unit": "str — e.g. 'invoice'",
    "monthly_outcomes": "int — projected successful outcomes/month (for $ savings)",
    "provider": "str — 'mock' | 'anthropic' | 'openai'",
    "baseline": {"name": "str", "model": "str", "strategy": "simple|verify",
                 "per_field_accuracy": "float (mock only)"},
    "candidate": {"name": "str", "model": "str", "strategy": "simple|verify",
                  "per_field_accuracy": "float (mock only)"},
    "n_invoices": "int — scenario set size",
    "repeats": "int — runs per invoice per version",
    "cost_tolerance": "float — allowed cost rise before FAIL (default 0.15)",
    "quality_tolerance": "float — allowed accuracy drop (default 0.02)",
    "dry_run": "bool — true = offline mock + no live platform writes",
}

# What the coded agent returns to Maestro.
OUTPUT_SCHEMA = {
    "verdict": "PASS | FAIL | NEEDS_REVIEW",
    "maestro_action": "promote | block | escalate",
    "report": "the full gate report (baseline vs candidate, cost-per-outcome, reasons)",
    "test_manager": "result of registering the Test Cloud execution",
    "hitl_task": "Action Center task payload (present when escalate/block), else null",
    "ledger_event": "the recorded savings-ledger event",
}
