"""App API Developer API Security Dashboard — unified security overview."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class SecurityDashboard:
    security_score: float = 100.0
    total_findings: int = 0
    critical_findings: int = 0
    high_findings: int = 0
    resolved_findings: int = 0
    active_api_keys: int = 0
    expired_keys: int = 0
    ip_rules: int = 0
    cors_policies: int = 0
    ssl_active: bool = True

class AppAPIDeveloperAPISecurityDashboard:
    def __init__(self) -> None:
        self._dashboards: dict[str, SecurityDashboard] = {}

    def update(self, installation_id: str, **kwargs) -> SecurityDashboard:
        if not installation_id: raise ValueError("installation_id is required")
        if installation_id not in self._dashboards:
            self._dashboards[installation_id] = SecurityDashboard()
        d = self._dashboards[installation_id]
        for k, v in kwargs.items():
            if hasattr(d, k): setattr(d, k, v)
        return d

    def get(self, installation_id: str) -> SecurityDashboard:
        return self._dashboards.get(installation_id, SecurityDashboard())

    def is_secure(self, installation_id: str) -> bool:
        d = self.get(installation_id)
        return d.critical_findings == 0 and d.security_score >= 80
