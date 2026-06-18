"""Zero-dependency UiPath auth via OAuth client-credentials.

Uses the External Application (client_id/secret in .env) to get a bearer token
from the tenant's identity endpoint. Stdlib only — works on any Python, no SDK
install needed. The token is used for local live verification and REST calls;
the deployed coded agent uses the ambient UiPath SDK auth instead.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request

from .config import UiPathConfig, load_config

# Orchestrator (jobs, test sets, Action Center tasks) + the granular Test Manager
# scopes actually granted to this app. NOTE: TM.Default is NOT a valid scope —
# Test Manager needs the granular TM.* scopes (probed against the tenant).
DEFAULT_SCOPE = ("OR.Default TM.Projects TM.TestCases TM.TestSets "
                 "TM.Requirements TM.Attachments TM.Users")


def get_token(config: UiPathConfig | None = None, scope: str | None = None,
              timeout: int = 30) -> str:
    config = config or load_config()
    if not config.configured:
        raise RuntimeError("UiPath config not set — fill .env (UIPATH_CLIENT_SECRET).")
    form = {
        "grant_type": "client_credentials",
        "client_id": config.client_id,
        "client_secret": config.client_secret,
        "scope": scope or DEFAULT_SCOPE,
    }
    req = urllib.request.Request(
        config.token_url, data=urllib.parse.urlencode(form).encode(),
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            # Cloudflare on staging blocks bare clients (error 1010) — present a browser UA.
            "User-Agent": ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                           "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"),
            "Accept": "application/json",
        })
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            payload = json.load(resp)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")[:300]
        raise RuntimeError(f"token request failed: HTTP {e.code} — {body}") from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"token request failed: {e.reason}") from e
    token = payload.get("access_token")
    if not token:
        raise RuntimeError(f"no access_token in response: {str(payload)[:200]}")
    return token
