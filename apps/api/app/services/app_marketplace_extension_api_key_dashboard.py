"""API Key Dashboard — overview of all API keys across extensions.

Aggregates key usage, expiry status, rotation needs, and security
alerts across all developer API keys.
"""
from __future__ import annotations
import time
from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class KeySummary:
    key_id: str
    extension_id: str
    name: str
    status: str  # active, expired, revoked
    usage_count: int
    last_used: float
    expires_at: float
    scopes: list[str] = field(default_factory=list)

    @property
    def days_until_expiry(self) -> int:
        if self.expires_at <= 0:
            return 999
        return max(0, int((self.expires_at - time.time()) / 86400))


class ExtensionApiKeyDashboardService:
    """Aggregates API key data across all developer extensions."""

    def __init__(self):
        self._keys: list[KeySummary] = []

    def add_key(self, key_id: str, extension_id: str, name: str,
                status: str, usage_count: int = 0,
                last_used: float = 0, expires_at: float = 0,
                scopes: list[str] | None = None) -> KeySummary:
        ks = KeySummary(key_id=key_id, extension_id=extension_id,
                        name=name, status=status, usage_count=usage_count,
                        last_used=last_used, expires_at=expires_at,
                        scopes=scopes or [])
        self._keys.append(ks)
        return ks

    def get_overview(self) -> dict:
        active = [k for k in self._keys if k.status == "active"]
        expiring_soon = [k for k in active if 0 < k.days_until_expiry <= 7]
        unused = [k for k in active if k.usage_count == 0]
        return {
            "total": len(self._keys),
            "active": len(active),
            "expired": sum(1 for k in self._keys if k.status == "expired"),
            "revoked": sum(1 for k in self._keys if k.status == "revoked"),
            "expiring_soon": len(expiring_soon),
            "unused": len(unused),
            "total_usage": sum(k.usage_count for k in self._keys),
        }

    def get_expiring(self, days: int = 7) -> list[KeySummary]:
        return [k for k in self._keys
                if k.status == "active" and 0 < k.days_until_expiry <= days]

    def get_by_extension(self, extension_id: str) -> list[KeySummary]:
        return [k for k in self._keys if k.extension_id == extension_id]

    def get_security_alerts(self) -> list[dict]:
        alerts = []
        for k in self._keys:
            if k.status == "active" and k.days_until_expiry <= 3:
                alerts.append({"key": k.name, "alert": "Expiring in <3 days", "severity": "high"})
            if k.status == "active" and k.usage_count == 0:
                alerts.append({"key": k.name, "alert": "Unused key — consider revoking", "severity": "medium"})
        return alerts
