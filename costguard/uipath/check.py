"""Verify the UiPath connection from .env (no secrets printed).

    python -m costguard.uipath.check

Reports config state and, if configured, requests a bearer token via
client-credentials to prove the External App + scopes work end-to-end.
"""

from __future__ import annotations

import sys

from .auth import get_token
from .config import load_config


def main() -> int:
    cfg = load_config()
    print("UiPath config:", cfg.redacted())
    if not cfg.configured:
        print("→ .env not complete yet. Set UIPATH_CLIENT_SECRET (and the rest), then re-run.")
        return 2
    try:
        token = get_token(cfg)
        print(f"✓ auth OK — bearer token received (length {len(token)}).")
        print(f"  base: {cfg.base_url}")
        print("  External App + scopes are valid. Ready to wire live (dry_run=False).")
        return 0
    except RuntimeError as e:
        print(f"✗ auth failed: {e}")
        print("  Check the rotated secret in .env, and that the External App has "
              "Orchestrator + TestManager scopes.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
