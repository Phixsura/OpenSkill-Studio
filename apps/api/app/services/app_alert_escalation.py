"""App Alert Escalation — escalate unacknowledged alerts to higher tiers.

Manages alert escalation for installed apps:
- Define escalation tiers with timeouts
- Auto-escalate unacknowledged alerts
- Track escalation history
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class EscalationTier:
    """An escalation tier."""

    tier: int
    name: str
    notify_targets: list[str]  # email, slack channel, etc.
    timeout_seconds: float  # time before escalating to next tier


@dataclass
class AlertEscalation:
    """An alert being escalated."""

    alert_id: str
    current_tier: int = 0
    acknowledged: bool = False
    created_at: float = field(default_factory=time.time)
    escalated_at: float | None = None
    acknowledged_by: str = ""


class AppAlertEscalation:
    """Escalate unacknowledged alerts to higher tiers."""

    def __init__(self) -> None:
        # installation_id → list[EscalationTier]
        self._tiers: dict[str, list[EscalationTier]] = {}
        # (installation_id, alert_id) → AlertEscalation
        self._alerts: dict[tuple[str, str], AlertEscalation] = {}

    def define_tiers(
        self, installation_id: str, tiers: list[dict]
    ) -> list[EscalationTier]:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not tiers:
            raise ValueError("at least one tier required")

        tier_objs = [
            EscalationTier(
                tier=i, name=t["name"],
                notify_targets=t["targets"],
                timeout_seconds=t["timeout_seconds"],
            )
            for i, t in enumerate(tiers)
        ]
        self._tiers[installation_id] = tier_objs
        return tier_objs

    def create_alert(
        self, installation_id: str, alert_id: str, now: float | None = None
    ) -> AlertEscalation:
        if not alert_id:
            raise ValueError("alert_id is required")

        key = (installation_id, alert_id)
        alert = AlertEscalation(alert_id=alert_id, created_at=now or time.time())
        self._alerts[key] = alert
        return alert

    def check_escalation(
        self, installation_id: str, alert_id: str, now: float | None = None
    ) -> EscalationTier | None:
        """Check if alert should escalate. Returns next tier or None."""
        now = now or time.time()
        key = (installation_id, alert_id)
        alert = self._alerts.get(key)
        if alert is None or alert.acknowledged:
            return None

        tiers = self._tiers.get(installation_id, [])
        if alert.current_tier >= len(tiers):
            return None

        current = tiers[alert.current_tier]
        ref_time = alert.escalated_at or alert.created_at
        if now - ref_time >= current.timeout_seconds:
            # Escalate
            alert.current_tier += 1
            alert.escalated_at = now
            if alert.current_tier < len(tiers):
                return tiers[alert.current_tier]
        return None

    def acknowledge(
        self, installation_id: str, alert_id: str, by: str
    ) -> AlertEscalation:
        key = (installation_id, alert_id)
        alert = self._alerts.get(key)
        if alert is None:
            raise KeyError(f"Alert {alert_id} not found")
        alert.acknowledged = True
        alert.acknowledged_by = by
        return alert

    def get_alert(self, installation_id: str, alert_id: str) -> AlertEscalation:
        key = (installation_id, alert_id)
        a = self._alerts.get(key)
        if a is None:
            raise KeyError(f"Alert {alert_id} not found")
        return a
