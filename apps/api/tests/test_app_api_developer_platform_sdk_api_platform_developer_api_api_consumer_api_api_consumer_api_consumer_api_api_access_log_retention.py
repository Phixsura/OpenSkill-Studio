import pytest
from datetime import datetime, timedelta
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_api_access_log_retention import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiAccessLogRetention, AccessLogEntry, RetentionConfig,
)

class TestConsumerApiAccessLogRetention:
    def _now(self):
        return datetime(2026, 6, 1)

    def test_append_and_query(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiAccessLogRetention()
        svc.append("inst-1", AccessLogEntry(log_id="l1", consumer_id="c1", method="GET", path="/api", status_code=200, timestamp=self._now()))
        logs = svc.query("inst-1", "c1")
        assert len(logs) == 1

    def test_filter_by_method(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiAccessLogRetention()
        svc.append("inst-1", AccessLogEntry(log_id="l1", consumer_id="c1", method="GET", path="/a", status_code=200, timestamp=self._now()))
        svc.append("inst-1", AccessLogEntry(log_id="l2", consumer_id="c1", method="POST", path="/b", status_code=201, timestamp=self._now()))
        assert len(svc.query("inst-1", "c1", method="POST")) == 1

    def test_cleanup(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiAccessLogRetention()
        svc.set_config("inst-1", RetentionConfig(consumer_id="c1", retention_days=7))
        svc.append("inst-1", AccessLogEntry(log_id="old", consumer_id="c1", method="GET", path="/", status_code=200, timestamp=self._now() - timedelta(days=10)))
        svc.append("inst-1", AccessLogEntry(log_id="new", consumer_id="c1", method="GET", path="/", status_code=200, timestamp=self._now()))
        removed = svc.cleanup("inst-1", "c1", self._now())
        assert removed == 1

    def test_max_entries(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiAccessLogRetention()
        svc.set_config("inst-1", RetentionConfig(consumer_id="c1", max_entries=3))
        for i in range(5):
            svc.append("inst-1", AccessLogEntry(log_id=f"l{i}", consumer_id="c1", method="GET", path="/", status_code=200, timestamp=self._now()))
        assert len(svc.query("inst-1", "c1", limit=100)) == 3

    def test_stats(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiAccessLogRetention()
        svc.append("inst-1", AccessLogEntry(log_id="l1", consumer_id="c1", method="GET", path="/", status_code=200, timestamp=self._now()))
        stats = svc.get_stats("inst-1", "c1", self._now())
        assert stats.total_entries == 1

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiAccessLogRetention()
        svc.append("inst-1", AccessLogEntry(log_id="l1", consumer_id="c1", method="GET", path="/", status_code=200, timestamp=self._now()))
        assert len(svc.query("inst-2", "c1")) == 0
