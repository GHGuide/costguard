"""CostGuard control tower — text rendering of the dashboard data model.

    python -m costguard.dashboard

Renders the savings ledger, the fleet view, and a per-agent cost-per-outcome
trend from a Ledger. The eventual UiPath App / web dashboard reads the same
ledger; this proves the numbers offline today.

The seeded history uses illustrative real-model dollar figures (the offline mock
gateway's token costs are intentionally tiny). The *ratios and the math* are
real; absolute $ become live once it runs on real models / UiPath.
"""

from __future__ import annotations

import os

from .ledger import Ledger

LEDGER_PATH = "data/ledger.json"

_BLOCKS = "▁▂▃▄▅▆▇█"


def _spark(values: list[float]) -> str:
    if not values:
        return ""
    lo, hi = min(values), max(values)
    if hi == lo:
        return _BLOCKS[0] * len(values)
    return "".join(_BLOCKS[int((v - lo) / (hi - lo) * (len(_BLOCKS) - 1))] for v in values)


def _usd(x: float) -> str:
    return f"${x:,.4f}" if x < 1 else f"${x:,.2f}"


def _mini_report(verdict: str, base_cps: float, cand_cps: float, acc_delta: float,
                 unit: str = "invoice") -> dict:
    """Minimal report shaped like report.build_report — enough for Ledger.record."""
    ratio = cand_cps / base_cps if base_cps else float("inf")
    return {
        "verdict": verdict, "outcome_unit": unit,
        "cost_ratio": round(ratio, 3), "accuracy_delta": acc_delta,
        "baseline": {"cost_per_success_usd": base_cps},
        "candidate": {"cost_per_success_usd": cand_cps},
    }


def seed_demo() -> Ledger:
    """A realistic first-month history for one agent: a blocked regression and a
    greenlit optimization. Numbers are illustrative real-model figures."""
    led = Ledger()
    agent, vol = "invoice-extractor", 50_000
    # v1 baseline ~ $0.012/invoice already in production.
    led.record(_mini_report("FAIL", 0.012, 0.087, +0.012), agent, "v2-verbose-prompt", "v1",
               vol, ts="2026-05-21T10:00:00+00:00")     # 7.25x regression -> BLOCKED (avoided)
    led.record(_mini_report("NEEDS_REVIEW", 0.012, 0.006, -0.035), agent, "v3-haiku-swap", "v1",
               vol, ts="2026-05-29T10:00:00+00:00")     # cheaper but quality dropped -> human
    led.record(_mini_report("PASS", 0.012, 0.008, -0.004), agent, "v4-tuned-prompt", "v1",
               vol, ts="2026-06-08T10:00:00+00:00")     # cheaper, quality flat -> ADOPTED (realized)
    return led


def render(led: Ledger) -> str:
    bar = "═" * 68
    out = [bar, "  CostGuard — Agent Cost & Efficiency Control Tower", bar]

    t = led.totals()
    out.append("  SAVINGS LEDGER")
    out.append(f"    avoided (regressions blocked):   {_usd(t['avoided_monthly_usd'])}/mo")
    out.append(f"    realized (optimizations adopted):{_usd(t['realized_monthly_usd'])}/mo")
    out.append(f"    ──────────────────────────────────────────────")
    out.append(f"    total impact:  {_usd(t['total_monthly_usd'])}/mo   "
               f"(~{_usd(t['total_annual_usd'])}/yr)")
    out.append(f"    {t['regressions_blocked']} regression(s) blocked across {t['gate_runs']} gate runs")
    out.append("")

    out.append("  FLEET")
    out.append("    {:<22}{:>16}{:>20}{:>14}".format("agent", "$/outcome", "proj. monthly", "last gate"))
    for r in led.fleet():
        out.append("    {:<22}{:>16}{:>20}{:>14}".format(
            r["agent"][:22], _usd(r["current_cost_per_outcome_usd"]),
            _usd(r["projected_monthly_spend_usd"]), r["last_verdict"]))
    out.append("")

    out.append("  COST-PER-OUTCOME TREND (per evaluated version)")
    for a in led.agents():
        tr = led.trend(a)
        spark = _spark([cps for _, _, cps, _ in tr])
        out.append(f"    {a}:  {spark}")
        for _, ver, cps, verdict in tr:
            mark = {"FAIL": "⛔ blocked", "PASS": "✅ adopted", "NEEDS_REVIEW": "🟡 review"}[verdict]
            out.append(f"        {ver:<20} {_usd(cps):>10}/outcome   {mark}")
    out.append(bar)
    return "\n".join(out)


def main() -> int:
    # Show real recorded gate runs if any exist, else the seeded illustrative history.
    led = Ledger.load(LEDGER_PATH) if os.path.exists(LEDGER_PATH) and Ledger.load(LEDGER_PATH).events \
        else seed_demo()
    print(render(led))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
