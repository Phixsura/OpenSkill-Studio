import pytest
from datetime import datetime
from app.services.app_api_developer_platform_sdk_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_endpoint_traffic_monitor import (
    AppAPIDeveloperPlatformSDKConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiEndpointTrafficMonitor, TrafficSnapshot,
)

class TestEndpointTrafficMonitor:
    def _now(self):
        return datetime(2026, 6, 1, 12, 0, 0)

    def test_record_and_summary(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiEndpointTrafficMonitor()
        svc.record_snapshot("inst-1", TrafficSnapshot(endpoint_path="/api/users", timestamp=self._now(), requests_per_second=50, active_connections=10, avg_latency_ms=80, error_count=2))
        summary = svc.get_summary("inst-1", "/api/users", self._now())
        assert summary.current_rps == 50 and summary.peak_rps == 50

    def test_peak_tracking(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiEndpointTrafficMonitor()
        svc.record_snapshot("inst-1", TrafficSnapshot(endpoint_path="/api", timestamp=self._now(), requests_per_second=30, active_connections=5, avg_latency_ms=50, error_count=0))
        svc.record_snapshot("inst-1", TrafficSnapshot(endpoint_path="/api", timestamp=self._now(), requests_per_second=100, active_connections=20, avg_latency_ms=60, error_count=0))
        svc.record_snapshot("inst-1", TrafficSnapshot(endpoint_path="/api", timestamp=self._now(), requests_per_second=50, active_connections=10, avg_latency_ms=55, error_count=0))
        summary = svc.get_summary("inst-1", "/api", self._now())
        assert summary.peak_rps == 100 and summary.current_rps == 50

    def test_spike_alert(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiEndpointTrafficMonitor()
        svc.set_thresholds("inst-1", "/api", rps_spike=50)
        svc.record_snapshot("inst-1", TrafficSnapshot(endpoint_path="/api", timestamp=self._now(), requests_per_second=80, active_connections=15, avg_latency_ms=50, error_count=0))
        summary = svc.get_summary("inst-1", "/api", self._now())
        assert any(a.alert_type == "spike" for a in summary.alerts)

    def test_latency_alert(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiEndpointTrafficMonitor()
        svc.set_thresholds("inst-1", "/api", latency_ms=200)
        svc.record_snapshot("inst-1", TrafficSnapshot(endpoint_path="/api", timestamp=self._now(), requests_per_second=10, active_connections=5, avg_latency_ms=500, error_count=0))
        summary = svc.get_summary("inst-1", "/api", self._now())
        assert any(a.alert_type == "high_latency" for a in summary.alerts)

    def test_empty(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiEndpointTrafficMonitor()
        summary = svc.get_summary("inst-1", "/missing", self._now())
        assert summary.current_rps == 0

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiEndpointTrafficMonitor()
        svc.record_snapshot("inst-1", TrafficSnapshot(endpoint_path="/api", timestamp=self._now(), requests_per_second=50, active_connections=10, avg_latency_ms=80, error_count=0))
        assert len(svc.list_endpoints("inst-2")) == 0
