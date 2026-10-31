import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_usage_alert_rule import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiUsageAlertRule, AlertRule,
)

class TestConsumerApiUsageAlertRule:
    def test_fire_on_threshold(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiUsageAlertRule()
        svc.add_rule("inst-1", AlertRule(rule_id="r1", consumer_id="c1", metric="error_rate", condition="gt", threshold=5.0, severity="critical"))
        fired = svc.evaluate("inst-1", "c1", {"error_rate": 10.0})
        assert len(fired) == 1 and fired[0].severity == "critical"

    def test_no_fire_below(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiUsageAlertRule()
        svc.add_rule("inst-1", AlertRule(rule_id="r1", consumer_id="c1", metric="error_rate", condition="gt", threshold=5.0))
        assert len(svc.evaluate("inst-1", "c1", {"error_rate": 3.0})) == 0

    def test_lt_condition(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiUsageAlertRule()
        svc.add_rule("inst-1", AlertRule(rule_id="r1", consumer_id="c1", metric="requests", condition="lt", threshold=10))
        assert len(svc.evaluate("inst-1", "c1", {"requests": 5})) == 1

    def test_invalid_metric(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiUsageAlertRule()
        with pytest.raises(ValueError, match="Invalid metric"):
            svc.add_rule("inst-1", AlertRule(rule_id="r1", consumer_id="c1", metric="bad", condition="gt", threshold=1))

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiUsageAlertRule()
        svc.add_rule("inst-1", AlertRule(rule_id="r1", consumer_id="c1", metric="requests", condition="gt", threshold=100))
        assert svc.rule_count("inst-2") == 0
