"""Register a CostGuard gate verdict as a UiPath Test Cloud test execution.

This is what makes CostGuard legitimately a Test Cloud (Track 3) solution: a
cost/efficiency regression is recorded as a first-class test result, not a side
report. Verdict maps to a Test Manager status:
    PASS -> Passed, FAIL -> Failed, NEEDS_REVIEW -> Blocked (awaiting a human).

dry_run (default) writes the exact payload to a local JSONL file so the whole
flow is verifiable offline. Live mode posts via the UiPath SDK's API client;
the endpoint path is confirmed at wire-up (guarded so offline never touches it).
"""

from __future__ import annotations

import json
import os

from .config import UiPathConfig, load_config

STATUS = {"PASS": "Passed", "FAIL": "Failed", "NEEDS_REVIEW": "Blocked"}


class TestManagerClient:
    def __init__(self, config: UiPathConfig | None = None, dry_run: bool = True,
                 dry_run_path: str = "data/test_manager_dryrun.jsonl"):
        self.config = config or load_config()
        self.dry_run = dry_run
        self.dry_run_path = dry_run_path

    def _payload(self, report: dict, project: str, test_case: str) -> dict:
        b, c = report["baseline"], report["candidate"]
        return {
            "project": project,
            "testCase": test_case,
            "status": STATUS[report["verdict"]],
            "name": f"cost-efficiency regression — {report['outcome_unit']}",
            "metrics": {
                "outcome_unit": report["outcome_unit"],
                "cost_ratio": report["cost_ratio"],
                "accuracy_delta": report["accuracy_delta"],
                "baseline_cost_per_success_usd": b["cost_per_success_usd"],
                "candidate_cost_per_success_usd": c["cost_per_success_usd"],
                "extra_cost_per_1000_outcomes_usd": report["extra_cost_per_1000_outcomes_usd"],
            },
            "log": " | ".join(report["reasons"]),
        }

    def register(self, report: dict, project: str = "CostGuard",
                 test_case: str = "cost-efficiency-regression") -> dict:
        payload = self._payload(report, project, test_case)
        if self.dry_run:
            os.makedirs(os.path.dirname(self.dry_run_path) or ".", exist_ok=True)
            with open(self.dry_run_path, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(payload) + "\n")
            return {"dry_run": True, "registered": True, "status": payload["status"],
                    "payload": payload}
        return self._post_live(payload)

    def _post_live(self, payload: dict) -> dict:
        """Live registration via the UiPath SDK API client. Endpoint confirmed at
        wire-up; guarded so it never runs offline."""
        if not self.config.configured:
            raise RuntimeError("UiPath config not set (.env). Cannot register live.")
        try:
            from uipath import UiPath  # lazy import; only needed live
        except ImportError as e:  # pragma: no cover
            raise ImportError("pip install uipath to register live test results") from e
        client = UiPath()  # picks up auth from `uip auth` / env
        # Test Manager isn't a first-class SDK service -> use the raw API client.
        # Path is confirmed against the tenant's Test Manager API at wire-up.
        resp = client.api_client.request(
            "POST", f"{self.config.base_url}/testmanager_/api/v1/testCaseExecutions",
            json=payload)
        return {"dry_run": False, "registered": True, "status": payload["status"],
                "response_status": getattr(resp, "status_code", None)}
