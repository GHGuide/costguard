"""The CostGuard ledger — the data model behind the dashboard.

Every gate run is recorded as a GateEvent. From that history the dashboard
derives the three things that make CostGuard *consistently* useful (not just a
demo screen):

  • a savings ledger  — money AVOIDED by blocking a cost regression, plus money
                        REALIZED by adopting a cheaper-but-equal version;
  • a cost-per-outcome trend per agent (drift you can see before it's a crisis);
  • a fleet view      — what each agent currently costs per business outcome.

Savings are expressed per month using each agent's projected outcome volume, so
a per-outcome delta becomes a real dollar figure finance recognises.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone


@dataclass
class GateEvent:
    ts: str                              # ISO timestamp
    agent: str
    version: str                         # the candidate version evaluated
    baseline_version: str
    verdict: str                         # PASS | FAIL | NEEDS_REVIEW
    outcome_unit: str
    cost_per_success_usd: float          # candidate
    baseline_cost_per_success_usd: float
    cost_ratio: float
    accuracy_delta: float
    monthly_outcomes: int
    monthly_cost_candidate_usd: float
    monthly_cost_baseline_usd: float
    monthly_delta_usd: float             # candidate - baseline (+ = more expensive)
    savings_usd: float                   # monthly $ saved by this event
    savings_kind: str                    # avoided | realized | pending | none


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class Ledger:
    def __init__(self, events: list[GateEvent] | None = None):
        self.events: list[GateEvent] = list(events or [])

    # --- persistence -------------------------------------------------------
    @classmethod
    def load(cls, path: str) -> "Ledger":
        with open(path, encoding="utf-8") as fh:
            return cls([GateEvent(**e) for e in json.load(fh)])

    def save(self, path: str) -> None:
        with open(path, "w", encoding="utf-8") as fh:
            json.dump([asdict(e) for e in self.events], fh, indent=2)

    # --- recording ---------------------------------------------------------
    def record(self, report: dict, agent: str, version: str, baseline_version: str,
               monthly_outcomes: int, ts: str | None = None) -> GateEvent:
        cps = report["candidate"]["cost_per_success_usd"]
        bcps = report["baseline"]["cost_per_success_usd"]
        mc = cps * monthly_outcomes
        mb = bcps * monthly_outcomes
        delta = mc - mb
        verdict = report["verdict"]

        if verdict == "FAIL":                      # regression blocked -> we avoided the extra spend
            kind, savings = "avoided", max(0.0, delta)
        elif verdict == "PASS" and delta < 0:      # cheaper-and-not-worse adopted -> realized savings
            kind, savings = "realized", -delta
        elif verdict == "NEEDS_REVIEW":
            kind, savings = "pending", 0.0
        else:
            kind, savings = "none", 0.0

        ev = GateEvent(
            ts=ts or _now_iso(), agent=agent, version=version,
            baseline_version=baseline_version, verdict=verdict,
            outcome_unit=report["outcome_unit"],
            cost_per_success_usd=cps, baseline_cost_per_success_usd=bcps,
            cost_ratio=report["cost_ratio"], accuracy_delta=report["accuracy_delta"],
            monthly_outcomes=monthly_outcomes,
            monthly_cost_candidate_usd=round(mc, 2), monthly_cost_baseline_usd=round(mb, 2),
            monthly_delta_usd=round(delta, 2), savings_usd=round(savings, 2), savings_kind=kind)
        self.events.append(ev)
        return ev

    # --- queries -----------------------------------------------------------
    def agents(self) -> list[str]:
        return sorted({e.agent for e in self.events})

    def for_agent(self, agent: str) -> list[GateEvent]:
        return [e for e in self.events if e.agent == agent]

    def latest(self, agent: str) -> GateEvent | None:
        evs = self.for_agent(agent)
        return evs[-1] if evs else None

    def current_cost_per_outcome(self, agent: str) -> float:
        """What the agent costs per outcome right now: the adopted candidate if
        the last gate PASSed, otherwise still the baseline (a blocked candidate
        never shipped)."""
        e = self.latest(agent)
        if e is None:
            return 0.0
        return e.cost_per_success_usd if e.verdict == "PASS" else e.baseline_cost_per_success_usd

    def trend(self, agent: str) -> list[tuple[str, str, float, str]]:
        """(ts, version, candidate cost-per-outcome, verdict) per evaluated version."""
        return [(e.ts, e.version, e.cost_per_success_usd, e.verdict) for e in self.for_agent(agent)]

    def totals(self) -> dict:
        avoided = sum(e.savings_usd for e in self.events if e.savings_kind == "avoided")
        realized = sum(e.savings_usd for e in self.events if e.savings_kind == "realized")
        total = avoided + realized
        return {
            "avoided_monthly_usd": round(avoided, 2),
            "realized_monthly_usd": round(realized, 2),
            "total_monthly_usd": round(total, 2),
            "total_annual_usd": round(total * 12, 2),
            "regressions_blocked": sum(1 for e in self.events if e.verdict == "FAIL"),
            "gate_runs": len(self.events),
        }

    def fleet(self) -> list[dict]:
        rows = []
        for a in self.agents():
            e = self.latest(a)
            cps = self.current_cost_per_outcome(a)
            rows.append({
                "agent": a,
                "outcome_unit": e.outcome_unit,
                "current_cost_per_outcome_usd": round(cps, 6),
                "projected_monthly_spend_usd": round(cps * e.monthly_outcomes, 2),
                "last_verdict": e.verdict,
            })
        return rows
