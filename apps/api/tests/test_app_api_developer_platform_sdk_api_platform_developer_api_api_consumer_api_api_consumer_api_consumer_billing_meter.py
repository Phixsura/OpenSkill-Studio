import pytest
from datetime import datetime, timedelta
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_billing_meter import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerBillingMeter, UsageEvent,
)

class TestConsumerBillingMeter:
    def _now(self):
        return datetime(2026, 6, 1, 12, 0, 0)

    def test_record_and_total(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerBillingMeter()
        svc.record("inst-1", "c1", UsageEvent(event_id="e1", metric="api_calls", quantity=10, timestamp=self._now()))
        svc.record("inst-1", "c1", UsageEvent(event_id="e2", metric="api_calls", quantity=5, timestamp=self._now()))
        assert svc.total_for_metric("inst-1", "c1", "api_calls") == 15

    def test_summarize(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerBillingMeter()
        svc.record("inst-1", "c1", UsageEvent(event_id="e1", metric="api_calls", quantity=10, timestamp=self._now()))
        svc.record("inst-1", "c1", UsageEvent(event_id="e2", metric="data_transfer", quantity=1024, timestamp=self._now()))
        summaries = svc.summarize("inst-1", "c1")
        assert len(summaries) == 2
        assert summaries[0].metric == "api_calls" and summaries[0].total == 10

    def test_usage_between(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerBillingMeter()
        svc.record("inst-1", "c1", UsageEvent(event_id="e1", metric="api_calls", quantity=1, timestamp=self._now()))
        svc.record("inst-1", "c1", UsageEvent(event_id="e2", metric="api_calls", quantity=1, timestamp=self._now() + timedelta(hours=2)))
        events = svc.usage_between("inst-1", "c1", self._now(), self._now() + timedelta(hours=1))
        assert len(events) == 1

    def test_negative_quantity(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerBillingMeter()
        with pytest.raises(ValueError, match="non-negative"):
            svc.record("inst-1", "c1", UsageEvent(event_id="e1", metric="x", quantity=-1, timestamp=self._now()))

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerBillingMeter()
        svc.record("inst-1", "c1", UsageEvent(event_id="e1", metric="api_calls", quantity=10, timestamp=self._now()))
        assert svc.total_for_metric("inst-2", "c1", "api_calls") == 0
