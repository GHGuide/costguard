"""Human-in-the-loop via UiPath Action Center.

On FAIL or NEEDS_REVIEW, CostGuard does not silently block or guess — it opens
an Action Center task so a human owns the high-impact call (promote / quarantine
/ override), with the full cost evidence attached. This is the accountability
the rules emphasise.

dry_run returns the task payload (verifiable offline). Live mode creates the
task via the SDK's Action Center service.
"""

from __future__ import annotations

from .config import UiPathConfig, load_config

# Which verdicts need a human.
ESCALATE_VERDICTS = {"FAIL", "NEEDS_REVIEW"}


def build_hitl_task(report: dict) -> dict:
    b, c = report["baseline"], report["candidate"]
    verdict = report["verdict"]
    priority = "High" if verdict == "FAIL" else "Medium"
    title = (f"CostGuard: {verdict} — {report['cost_ratio']:.2f}x cost on "
             f"'{c['name']}' vs '{b['name']}'")
    return {
        "title": title,
        "priority": priority,
        "data": {
            "verdict": verdict,
            "outcome_unit": report["outcome_unit"],
            "cost_ratio": report["cost_ratio"],
            "accuracy_delta": report["accuracy_delta"],
            "extra_cost_per_1000_outcomes_usd": report["extra_cost_per_1000_outcomes_usd"],
            "baseline_cost_per_success_usd": b["cost_per_success_usd"],
            "candidate_cost_per_success_usd": c["cost_per_success_usd"],
            "reasons": report["reasons"],
        },
        "actions": ["Approve & promote", "Reject & quarantine", "Override (ship anyway)"],
    }


class ActionCenterClient:
    def __init__(self, config: UiPathConfig | None = None, dry_run: bool = True):
        self.config = config or load_config()
        self.dry_run = dry_run

    def create_task(self, report: dict) -> dict | None:
        if report["verdict"] not in ESCALATE_VERDICTS:
            return None  # PASS needs no human
        task = build_hitl_task(report)
        if self.dry_run:
            return {"dry_run": True, "created": True, "task": task}
        return self._create_live(task)

    def _create_live(self, task: dict) -> dict:
        if not self.config.configured:
            raise RuntimeError("UiPath config not set (.env). Cannot create task live.")
        try:
            from uipath import UiPath  # lazy import
        except ImportError as e:  # pragma: no cover
            raise ImportError("pip install uipath to create Action Center tasks live") from e
        client = UiPath()
        created = client.tasks.create(
            title=task["title"], priority=task["priority"], data=task["data"])
        return {"dry_run": False, "created": True, "task_id": getattr(created, "id", None)}
