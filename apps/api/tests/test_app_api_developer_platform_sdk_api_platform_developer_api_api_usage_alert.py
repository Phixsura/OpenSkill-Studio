import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_usage_alert import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiUsageAlert, AlertRule, AlertSeverity, AlertStatus,
)

class TestApiUsageAlert:
    def test_fire_on_threshold(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiUsageAlert()
        svc.add_rule("inst-1", AlertRule(rule_id="r1", metric="error_rate", operator="gt", threshold=5.0, severity=AlertSeverity.CRITICAL, cooldown_s=0))
        fired = svc.evaluate("inst-1", {"error_rate": 10.0})
        assert len(fired) == 1
        assert fired[0].severity == AlertSeverity.CRITICAL

    def test_no_fire_below(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiUsageAlert()
        svc.add_rule("inst-1", AlertRule(rule_id="r1", metric="error_rate", operator="gt", threshold=5.0, cooldown_s=0))
        fired = svc.evaluate("inst-1", {"error_rate": 3.0})
        assert len(fired) == 0

    def test_cooldown(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiUsageAlert()
        svc.add_rule("inst-1", AlertRule(rule_id="r1", metric="request_count", operator="gt", threshold=100, cooldown_s=9999))
        svc.evaluate("inst-1", {"request_count": 200})
        fired2 = svc.evaluate("inst-1", {"request_count": 200})
        assert len(fired2) == 0  # cooldown blocks

    def test_acknowledge(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiUsageAlert()
        svc.add_rule("inst-1", AlertRule(rule_id="r1", metric="latency_p99", operator="gte", threshold=500, cooldown_s=0))
        fired = svc.evaluate("inst-1", {"latency_p99": 600})
        svc.acknowledge("inst-1", fired[0].alert_id)
        assert len(svc.active_alerts("inst-1")) == 0

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiUsageAlert()
        svc.add_rule("inst-1", AlertRule(rule_id="r1", metric="error_rate", operator="gt", threshold=1, cooldown_s=0))
        svc.evaluate("inst-1", {"error_rate": 10})
        assert svc.alert_count("inst-2") == 0
