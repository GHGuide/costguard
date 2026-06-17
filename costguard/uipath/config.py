"""UiPath connection config, read from .env. Secrets are never logged or returned
in plain text — `redacted()` reports only whether each value is set.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from ..env import load_dotenv


@dataclass
class UiPathConfig:
    url: str = ""
    org: str = ""
    tenant: str = ""
    client_id: str = ""
    client_secret: str = ""

    @property
    def configured(self) -> bool:
        return all([self.url, self.org, self.tenant, self.client_id, self.client_secret])

    @property
    def base_url(self) -> str:
        return f"{self.url.rstrip('/')}/{self.org}/{self.tenant}"

    @property
    def token_url(self) -> str:
        return f"{self.url.rstrip('/')}/identity_/connect/token"

    def redacted(self) -> dict:
        return {
            "url": self.url or "(unset)",
            "org": self.org or "(unset)",
            "tenant": self.tenant or "(unset)",
            "client_id": "set" if self.client_id else "(unset)",
            "client_secret": "set" if self.client_secret else "(unset)",
            "configured": self.configured,
        }


def load_config() -> UiPathConfig:
    load_dotenv()
    return UiPathConfig(
        url=os.environ.get("UIPATH_URL", ""),
        org=os.environ.get("UIPATH_ORG", ""),
        tenant=os.environ.get("UIPATH_TENANT", ""),
        client_id=os.environ.get("UIPATH_CLIENT_ID", ""),
        client_secret=os.environ.get("UIPATH_CLIENT_SECRET", ""),
    )
