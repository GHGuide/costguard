"""UiPath integration-layer tests (all dry-run / offline).
Run: python tests/test_uipath.py (or pytest)."""

from __future__ import annotations

import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from costguard.uipath.action_center import ActionCenterClient, build_hitl_task
from costguard.uipath.config import UiPathConfig, load_config
from costguard.uipath.maestro_contract import decide_action
from costguard.uipath.test_manager import STATUS, TestManagerClient


def _report(verdict="FAIL"):
    return {
        "verdict": verdict, "outcome_unit": "invoice", "cost_ratio": 7.27,
        "accuracy_delta": 0.044, "extra_cost_per_1000_outcomes_usd": 6.11,
        "reasons": ["cost per successful invoice rose 7.27x"],
        "baseline": {"name": "v1", "cost_per_success_usd": 0.001},
        "candidate": {"name": "v2", "cost_per_success_usd": 0.0071},
    }


def test_decision_mapping():
    assert decide_action("PASS") == "promote"
    assert decide_action("FAIL") == "block"
    assert decide_action("NEEDS_REVIEW") == "escalate"


def test_config_redacts_secrets():
    cfg = UiPathConfig(url="u", org="o", tenant="t", client_id="id", client_secret="shh")
    r = cfg.redacted()
    assert r["client_secret"] == "set" and "shh" not in str(r)
    assert UiPathConfig().configured is False


def test_test_manager_dry_run_writes_and_maps_status():
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "tm.jsonl")
        res = TestManagerClient(dry_run=True, dry_run_path=path).register(_report("FAIL"))
        assert res["dry_run"] and res["status"] == STATUS["FAIL"] == "Failed"
        assert os.path.exists(path)


def test_hitl_built_for_fail_not_for_pass():
    assert ActionCenterClient(dry_run=True).create_task(_report("PASS")) is None
    task = ActionCenterClient(dry_run=True).create_task(_report("FAIL"))
    assert task["created"] and "Approve & promote" in task["task"]["actions"]


def test_hitl_payload_has_evidence():
    t = build_hitl_task(_report("NEEDS_REVIEW"))
    assert t["priority"] == "Medium"
    assert "cost_ratio" in t["data"] and t["data"]["reasons"]


def test_get_token_requires_config():
    from costguard.uipath.auth import get_token
    from costguard.uipath.config import UiPathConfig
    raised = False
    try:
        get_token(UiPathConfig())  # empty config -> no network call
    except RuntimeError:
        raised = True
    assert raised


def test_run_gate_end_to_end_dry_run():
    # full coded-agent path on the mock provider, isolated ledger
    import costguard.uipath.coded_agent as ca
    with tempfile.TemporaryDirectory() as d:
        ca.LEDGER_PATH = os.path.join(d, "ledger.json")
        tm_path = os.path.join(d, "tm.jsonl")
        inp = dict(ca.DEMO_INPUT)
        # route the test-manager dry-run file into the temp dir via monkeypatch
        orig = TestManagerClient.__init__

        def patched(self, config=None, dry_run=True, dry_run_path=tm_path):
            orig(self, config=config, dry_run=dry_run, dry_run_path=dry_run_path)
        TestManagerClient.__init__ = patched
        try:
            out = ca.run_gate(inp)
        finally:
            TestManagerClient.__init__ = orig
    assert out["verdict"] == "FAIL"
    assert out["maestro_action"] == "block"
    assert out["test_manager"]["status"] == "Failed"
    assert out["hitl_task"] is not None
    assert out["ledger_event"]["savings_kind"] == "avoided"


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    failed = 0
    for fn in fns:
        try:
            fn()
            print(f"PASS {fn.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"FAIL {fn.__name__}: {e}")
    print(f"\n{len(fns) - failed}/{len(fns)} passed")
    raise SystemExit(1 if failed else 0)
