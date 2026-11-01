import pytest
from datetime import datetime
from app.services.app_api_developer_platform_sdk_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_api_consumer_api_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_api_consumer_api_consumer_api_consumer_api_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_api_consumer_api_consumer_api_api_consumer_api_consumer_api_api_consumer_api_consumer_api_api_consumer_api_consumer_api_api_consumer_api_consumer_api_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_api_consumer_api_consumer_api_consumer_api_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_api_consumer_api_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_api_consumer_api_consumer_api_api_consumer_api_consumer_api_api_consumer_api_consumer_api_api_consumer_api_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_api_consumer_api_consumer_api_consumer_api_api_consumer_api_api_request_log_search import (
    AppAPIDeveloperPlatformSDKConsumerApiRequestLogSearch, LogEntry,
)

class TestRequestLogSearch:
    def _now(self):
        return datetime(2026, 6, 1)

    def test_append_and_search(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiRequestLogSearch()
        svc.append("inst-1", LogEntry(log_id="l1", consumer_id="c1", method="GET", path="/api/users", status_code=200, latency_ms=50, timestamp=self._now()))
        result = svc.search("inst-1", "c1", "users")
        assert result.total_matches == 1

    def test_filter_by_status(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiRequestLogSearch()
        svc.append("inst-1", LogEntry(log_id="l1", consumer_id="c1", method="GET", path="/api", status_code=200, latency_ms=50, timestamp=self._now()))
        svc.append("inst-1", LogEntry(log_id="l2", consumer_id="c1", method="GET", path="/api", status_code=500, latency_ms=100, timestamp=self._now()))
        assert svc.search("inst-1", "c1", "", status_code=500).total_matches == 1

    def test_filter_by_method(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiRequestLogSearch()
        svc.append("inst-1", LogEntry(log_id="l1", consumer_id="c1", method="GET", path="/api", status_code=200, latency_ms=50, timestamp=self._now()))
        svc.append("inst-1", LogEntry(log_id="l2", consumer_id="c1", method="POST", path="/api", status_code=201, latency_ms=80, timestamp=self._now()))
        assert svc.search("inst-1", "c1", "", method="POST").total_matches == 1

    def test_body_search(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiRequestLogSearch()
        svc.append("inst-1", LogEntry(log_id="l1", consumer_id="c1", method="POST", path="/api/orders", status_code=201, latency_ms=80, body_preview='{"item":"widget"}', timestamp=self._now()))
        assert svc.search("inst-1", "c1", "widget").total_matches == 1

    def test_recent(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiRequestLogSearch()
        svc.append("inst-1", LogEntry(log_id="l1", consumer_id="c1", method="GET", path="/a", status_code=200, latency_ms=50, timestamp=self._now()))
        svc.append("inst-1", LogEntry(log_id="l2", consumer_id="c1", method="GET", path="/b", status_code=200, latency_ms=50, timestamp=self._now()))
        recent = svc.get_recent("inst-1", "c1")
        assert len(recent) == 2

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiRequestLogSearch()
        svc.append("inst-1", LogEntry(log_id="l1", consumer_id="c1", method="GET", path="/api", status_code=200, latency_ms=50, timestamp=self._now()))
        assert svc.search("inst-2", "c1", "api").total_matches == 0
