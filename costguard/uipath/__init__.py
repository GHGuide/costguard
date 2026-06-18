"""UiPath integration layer for CostGuard.

Drop-in adapters that wrap the CostGuard engine for the UiPath platform:
  • coded_agent  — the coded-agent entrypoint (input -> run gate -> output)
  • test_manager — register the gate verdict as a Test Cloud test execution
  • action_center— build the human-in-the-loop task for FAIL / NEEDS_REVIEW
  • maestro_contract — the in/out JSON contract + verdict->action decision
  • config       — reads UiPath creds from .env (never logs secrets)

Everything runs OFFLINE in dry-run mode (the default). When UiPath creds are in
.env and dry_run=False, the same calls hit the live platform. This is the
"flip the switch" boundary: the engine and these contracts are already proven;
going live changes only the transport.
"""

from .config import UiPathConfig, load_config
from .auth import get_token
from .maestro_contract import decide_action, INPUT_SCHEMA, OUTPUT_SCHEMA
from .test_manager import TestManagerClient
from .action_center import build_hitl_task, ActionCenterClient
from .coded_agent import run_gate

__all__ = [
    "UiPathConfig", "load_config", "get_token",
    "decide_action", "INPUT_SCHEMA", "OUTPUT_SCHEMA",
    "TestManagerClient", "build_hitl_task", "ActionCenterClient", "run_gate",
]
