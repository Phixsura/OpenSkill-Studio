import pytest
from datetime import datetime, timedelta
from app.services.app_api_developer_platform_sdk_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_endpoint_discovery import (
    AppAPIDeveloperPlatformSDKConsumerApiEndpointDiscovery,
)

class TestEndpointDiscovery:
    def _now(self):
        return datetime(2026, 6, 1, 12, 0, 0)

    def test_auto_discover(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiEndpointDiscovery()
        svc.record_request("inst-1", "GET", "/api/users", 50, self._now())
        svc.record_request("inst-1", "POST", "/api/orders", 80, self._now())
        report = svc.get_report("inst-1", now=self._now())
        assert report.total_discovered == 2 and report.undocumented == 2

    def test_running_avg_latency(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiEndpointDiscovery()
        svc.record_request("inst-1", "GET", "/api", 100, self._now())
        svc.record_request("inst-1", "GET", "/api", 200, self._now())
        eps = svc.list_all("inst-1")
        assert 149 < eps[0].avg_latency_ms < 151

    def test_mark_documented(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiEndpointDiscovery()
        svc.record_request("inst-1", "GET", "/api/users", 50, self._now())
        svc.mark_documented("inst-1", "GET", "/api/users")
        report = svc.get_report("inst-1", now=self._now())
        assert report.documented == 1

    def test_new_endpoints(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiEndpointDiscovery()
        svc.record_request("inst-1", "GET", "/old", 50, self._now() - timedelta(days=30))
        svc.record_request("inst-1", "GET", "/new", 50, self._now())
        report = svc.get_report("inst-1", since_days=7, now=self._now())
        assert len(report.new_endpoints) == 1 and report.new_endpoints[0].path == "/new"

    def test_request_count(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiEndpointDiscovery()
        for _ in range(5):
            svc.record_request("inst-1", "GET", "/api", 50, self._now())
        assert svc.list_all("inst-1")[0].request_count == 5

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiEndpointDiscovery()
        svc.record_request("inst-1", "GET", "/api", 50, self._now())
        assert len(svc.list_all("inst-2")) == 0
