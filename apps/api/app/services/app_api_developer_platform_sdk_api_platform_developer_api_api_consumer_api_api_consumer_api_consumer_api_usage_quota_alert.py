"""Consumer API Usage Quota Alert — alert when consumers approach quota limits."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
import structlog

log = structlog.get_logger()

@dataclass
class QuotaAlertRule:
    rule_id: str
    consumer_id: str
    metric: str  # "requests", "bandwidth", "compute"
    threshold_pct: float  # 0-100, alert when usage exceeds this %
    notify_channels: list[str] = field(default_factory=list)  # ["email", "webhook", "slack"]
    enabled: bool = True

@dataclass
class QuotaAlert:
    alert_id: str
    rule_id: str
    consumer_id: str
    metric: str
    current_usage: float
    quota_limit: float
    usage_pct: float
    triggered_at: datetime

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiUsageQuotaAlert:
    def __init__(self) -> None:
        self._rules: dict[tuple[str, str], QuotaAlertRule] = {}
        self._alerts: dict[tuple[str, str], list[QuotaAlert]] = {}  # (inst, consumer)

    def add_rule(self, installation_id: str, rule: QuotaAlertRule) -> QuotaAlertRule:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not (0 < rule.threshold_pct <= 100):
            raise ValueError("threshold_pct must be between 0 and 100")
        if rule.metric not in ("requests", "bandwidth", "compute"):
            raise ValueError(f"Invalid metric: {rule.metric}")
        self._rules[(installation_id, rule.rule_id)] = rule
        return rule

    def evaluate(self, installation_id: str, consumer_id: str, metric: str, current: float, limit: float, now: datetime) -> QuotaAlert | None:
        if limit <= 0:
            return None
        pct = (current / limit) * 100
        # Find matching enabled rule
        for (inst, _), rule in self._rules.items():
            if inst != installation_id or rule.consumer_id != consumer_id or rule.metric != metric or not rule.enabled:
                continue
            if pct >= rule.threshold_pct:
                alert = QuotaAlert(alert_id=f"qa-{rule.rule_id}-{now.isoformat()}", rule_id=rule.rule_id, consumer_id=consumer_id, metric=metric, current_usage=current, quota_limit=limit, usage_pct=round(pct, 1), triggered_at=now)
                key = (installation_id, consumer_id)
                if key not in self._alerts:
                    self._alerts[key] = []
                self._alerts[key].append(alert)
                log.info("quota_alert", installation_id=installation_id, consumer=consumer_id, metric=metric, pct=round(pct, 1))
                return alert
        return None

    def get_alerts(self, installation_id: str, consumer_id: str, limit: int = 20) -> list[QuotaAlert]:
        return self._alerts.get((installation_id, consumer_id), [])[-limit:]

    def list_rules(self, installation_id: str, consumer_id: str | None = None) -> list[QuotaAlertRule]:
        rules = [r for (inst, _), r in self._rules.items() if inst == installation_id]
        if consumer_id:
            rules = [r for r in rules if r.consumer_id == consumer_id]
        return rules
