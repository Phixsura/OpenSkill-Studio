import pytest
from datetime import datetime
from app.services.app_api_developer_platform_sdk_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_api_consumer_api_alert_rule_engine import (
    AppAPIDeveloperPlatformSDKConsumerApiAlertRuleEngine, AlertRule, AlertCondition,
)

class TestAlertRuleEngine:
    def _now(self):
        return datetime(2026, 6, 1)

    def test_rule_triggers(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiAlertRuleEngine()
        svc.add_rule("inst-1", AlertRule(rule_id="r1", name="High Errors", conditions=[AlertCondition(metric="error_rate", operator="gt", threshold=5.0)], severity="critical"))
        triggered = svc.evaluate("inst-1", {"error_rate": 8.0}, self._now())
        assert len(triggered) == 1 and triggered[0].severity == "critical"

    def test_rule_not_triggered(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiAlertRuleEngine()
        svc.add_rule("inst-1", AlertRule(rule_id="r1", name="High Errors", conditions=[AlertCondition(metric="error_rate", operator="gt", threshold=5.0)]))
        assert len(svc.evaluate("inst-1", {"error_rate": 2.0}, self._now())) == 0

    def test_multi_condition(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiAlertRuleEngine()
        svc.add_rule("inst-1", AlertRule(rule_id="r1", name="Bad", conditions=[
            AlertCondition(metric="error_rate", operator="gt", threshold=1.0),
            AlertCondition(metric="latency_p99", operator="gt", threshold=500),
        ]))
        assert len(svc.evaluate("inst-1", {"error_rate": 5, "latency_p99": 800}, self._now())) == 1
        assert len(svc.evaluate("inst-1", {"error_rate": 5, "latency_p99": 200}, self._now())) == 0

    def test_disabled_skipped(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiAlertRuleEngine()
        svc.add_rule("inst-1", AlertRule(rule_id="r1", name="X", conditions=[AlertCondition(metric="error_rate", operator="gt", threshold=0)], enabled=False))
        assert len(svc.evaluate("inst-1", {"error_rate": 100}, self._now())) == 0

    def test_invalid_operator(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiAlertRuleEngine()
        with pytest.raises(ValueError, match="Invalid operator"):
            svc.add_rule("inst-1", AlertRule(rule_id="r1", name="X", conditions=[AlertCondition(metric="x", operator="like", threshold=0)]))

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiAlertRuleEngine()
        svc.add_rule("inst-1", AlertRule(rule_id="r1", name="X", conditions=[AlertCondition(metric="error_rate", operator="gt", threshold=0)]))
        assert len(svc.evaluate("inst-2", {"error_rate": 100}, self._now())) == 0
