"""App API Developer API Key Dashboard — comprehensive key management overview."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class APIKeyDashboard:
    total_keys: int = 0
    active_keys: int = 0
    expired_keys: int = 0
    revoked_keys: int = 0
    total_requests_today: int = 0
    keys_expiring_soon: int = 0

class AppAPIDeveloperAPIKeyDashboard:
    def __init__(self) -> None:
        self._dashboards: dict[str, APIKeyDashboard] = {}

    def update(self, installation_id: str, **kwargs) -> APIKeyDashboard:
        if not installation_id: raise ValueError("installation_id is required")
        if installation_id not in self._dashboards:
            self._dashboards[installation_id] = APIKeyDashboard()
        d = self._dashboards[installation_id]
        for k, v in kwargs.items():
            if hasattr(d, k): setattr(d, k, v)
        return d

    def get(self, installation_id: str) -> APIKeyDashboard:
        return self._dashboards.get(installation_id, APIKeyDashboard())
