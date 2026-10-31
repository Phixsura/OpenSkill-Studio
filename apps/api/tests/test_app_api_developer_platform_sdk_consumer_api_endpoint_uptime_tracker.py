import pytest
from datetime import datetime
from app.services.app_api_developer_platform_sdk_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_endpoint_uptime_tracker import (
    AppAPIDeveloperPlatformSDKConsumerApiEndpointUptimeTracker, UptimeCheck,
)

class TestEndpointUptimeTracker:
    def _now(self):
        return datetime(2026, 6, 1)

    def test_all_up(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiEndpointUptimeTracker()
        for _ in range(10):
            svc.record_check("inst-1", UptimeCheck(endpoint_path="/api", is_up=True, response_time_ms=50, status_code=200, timestamp=self._now()))
        report = svc.get_report("inst-1", "/api")
        assert report.uptime_pct == 100 and report.current_status == "up"

    def test_some_down(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiEndpointUptimeTracker()
        for _ in range(8):
            svc.record_check("inst-1", UptimeCheck(endpoint_path="/api", is_up=True, response_time_ms=50, timestamp=self._now()))
        for _ in range(2):
            svc.record_check("inst-1", UptimeCheck(endpoint_path="/api", is_up=False, response_time_ms=0, timestamp=self._now()))
        report = svc.get_report("inst-1", "/api")
        assert report.uptime_pct == 80.0 and report.down_count == 2

    def test_current_status_down(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiEndpointUptimeTracker()
        svc.record_check("inst-1", UptimeCheck(endpoint_path="/api", is_up=True, response_time_ms=50, timestamp=self._now()))
        svc.record_check("inst-1", UptimeCheck(endpoint_path="/api", is_up=False, response_time_ms=0, timestamp=self._now()))
        assert svc.get_report("inst-1", "/api").current_status == "down"

    def test_avg_response_time(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiEndpointUptimeTracker()
        svc.record_check("inst-1", UptimeCheck(endpoint_path="/api", is_up=True, response_time_ms=100, timestamp=self._now()))
        svc.record_check("inst-1", UptimeCheck(endpoint_path="/api", is_up=True, response_time_ms=200, timestamp=self._now()))
        assert svc.get_report("inst-1", "/api").avg_response_ms == 150.0

    def test_empty(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiEndpointUptimeTracker()
        assert svc.get_report("inst-1", "/api").total_checks == 0

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiEndpointUptimeTracker()
        svc.record_check("inst-1", UptimeCheck(endpoint_path="/api", is_up=True, response_time_ms=50, timestamp=self._now()))
        assert len(svc.list_endpoints("inst-2")) == 0
