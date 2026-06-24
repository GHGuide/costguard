"""Register a CostGuard verdict as a REAL test result in UiPath Test Cloud.

This runs test case CG:1 in the CostGuard Test Manager project and records the
gate's verdict (PASS->Passed, FAIL->Failed, NEEDS_REVIEW->Restricted) with a link
back to the evidence — so the cost regression shows up as a first-class Test Cloud
result, not just a JSON file.

    uv run --with uipath python -m costguard.uipath.register_result            # uses docs/live-uipath-result.json
    uv run --with uipath python -m costguard.uipath.register_result FAIL       # force a verdict

Prereq (one-time): the External Application must have a Test Manager *execution*
scope. Without it, `testcases run` returns HTTP 403 and this script prints the exact
remediation. Everything else (login, project, test case CG:1) is already in place.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys

PROJECT = "CG"
TEST_CASE_ID = "f9e69f64-c850-0a00-bef7-0b49c7825d5d"  # CG:1
REPO = "https://github.com/GHGuide/costguard"
RESULT_MAP = {"PASS": "Passed", "FAIL": "Failed", "NEEDS_REVIEW": "Restricted"}


def _uip(args: list[str]) -> tuple[int, str]:
    proc = subprocess.run(["uip", *args], capture_output=True, text=True)
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def _json_tail(text: str) -> dict:
    """uip prints log lines then a JSON envelope; grab the last {...} block."""
    matches = re.findall(r"\{.*\}", text, re.DOTALL)
    for m in reversed(matches):
        try:
            return json.loads(m)
        except ValueError:
            continue
    return {}


def main(argv: list[str]) -> int:
    verdict = argv[1] if len(argv) > 1 else None
    if not verdict:
        path = "docs/live-uipath-result.json"
        verdict = (json.load(open(path, encoding="utf-8")).get("verdict")
                   if os.path.exists(path) else "FAIL")
    result = RESULT_MAP.get(verdict, "Failed")
    print(f"Registering CG:1 → {verdict} ({result}) in Test Cloud …")

    rc, out = _uip(["tm", "testcases", "run", "--project-key", PROJECT,
                    "--test-case-id", TEST_CASE_ID, "--execution-type", "manual",
                    "--name", f"CostGuard gate — {verdict}", "--output", "json"])
    if "403" in out or "Forbidden" in out:
        print("\n  ⛔ Blocked by a missing scope (HTTP 403).")
        print("  Add a Test Manager *execution* scope to the External Application, then re-run:")
        print("    UiPath Admin → External Applications → (this app) → Scopes →")
        print("    add  TM.TestSetExecutions  and  TM.TestCaseExecutions  → Save.")
        print("  Then: uv run --with uipath python -m costguard.uipath.register_result")
        return 2
    if rc != 0:
        print("  run failed:\n" + out[-600:])
        return 1

    execution_id = _json_tail(out).get("Id") or _json_tail(out).get("ExecutionId")
    if not execution_id:
        print("  could not read execution id from:\n" + out[-600:])
        return 1
    print(f"  execution {execution_id} started")

    rc, out = _uip(["tm", "testcaselog", "finish", "--project-key", PROJECT,
                    "--execution-id", execution_id, "--test-case-id", TEST_CASE_ID,
                    "--result", result, "--detail-link", REPO, "--output", "table"])
    if rc != 0:
        print("  finish failed:\n" + out[-600:])
        return 1
    print(f"  ✅ recorded {result} on CG:1 — visible in Test Cloud / Test Manager.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
