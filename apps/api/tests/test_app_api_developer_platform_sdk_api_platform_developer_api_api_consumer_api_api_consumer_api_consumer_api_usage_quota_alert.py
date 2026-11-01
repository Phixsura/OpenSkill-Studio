import pytest
from datetime import datetime
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_usage_quota_alert import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiUsageQuotaAlert, QuotaAlertRule,
)

class TestConsumerApiUsageQuotaAlert:
    def _now(self):
        return datetime(2026, 6, 1)

    def test_alert_triggered(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiUsageQuotaAlert()
        svc.add_rule("inst-1", QuotaAlertRule(rule_id="r1", consumer_id="c1", metric="requests", threshold_pct=80))
        alert = svc.evaluate("inst-1", "c1", "requests", 850, 1000, self._now())
        assert alert is not None and alert.usage_pct == 85.0

    def test_below_threshold(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiUsageQuotaAlert()
        svc.add_rule("inst-1", QuotaAlertRule(rule_id="r1", consumer_id="c1", metric="requests", threshold_pct=90))
        alert = svc.evaluate("inst-1", "c1", "requests", 500, 1000, self._now())
        assert alert is None

    def test_disabled_rule(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiUsageQuotaAlert()
        svc.add_rule("inst-1", QuotaAlertRule(rule_id="r1", consumer_id="c1", metric="requests", threshold_pct=50, enabled=False))
        alert = svc.evaluate("inst-1", "c1", "requests", 900, 1000, self._now())
        assert alert is None

    def test_alerts_stored(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiUsageQuotaAlert()
        svc.add_rule("inst-1", QuotaAlertRule(rule_id="r1", consumer_id="c1", metric="requests", threshold_pct=80))
        svc.evaluate("inst-1", "c1", "requests", 900, 1000, self._now())
        alerts = svc.get_alerts("inst-1", "c1")
        assert len(alerts) == 1

    def test_invalid_threshold(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiUsageQuotaAlert()
        with pytest.raises(ValueError, match="threshold_pct"):
            svc.add_rule("inst-1", QuotaAlertRule(rule_id="r1", consumer_id="c1", metric="requests", threshold_pct=0))

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiUsageQuotaAlert()
        svc.add_rule("inst-1", QuotaAlertRule(rule_id="r1", consumer_id="c1", metric="requests", threshold_pct=80))
        assert len(svc.list_rules("inst-2")) == 0
