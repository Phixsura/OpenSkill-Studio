import pytest
from datetime import datetime
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_api_consumer_api_endpoint_sla_monitor import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiEndpointSlaMonitor, SLATarget, SLAMeasurement,
)

class TestConsumerApiEndpointSlaMonitor:
    def _now(self):
        return datetime(2026, 6, 1)

    def test_in_compliance(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiEndpointSlaMonitor()
        svc.set_target("inst-1", SLATarget(endpoint_path="/api", availability_pct=99.9, latency_p99_ms=500))
        svc.record("inst-1", SLAMeasurement(endpoint_path="/api", timestamp=self._now(), availability_pct=99.99, latency_p99_ms=200, error_rate_pct=0.01, request_count=10000))
        report = svc.check_compliance("inst-1", "/api")
        assert report.in_compliance

    def test_breach(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiEndpointSlaMonitor()
        svc.set_target("inst-1", SLATarget(endpoint_path="/api", availability_pct=99.9))
        svc.record("inst-1", SLAMeasurement(endpoint_path="/api", timestamp=self._now(), availability_pct=98.0, latency_p99_ms=100, error_rate_pct=0.01, request_count=1000))
        report = svc.check_compliance("inst-1", "/api")
        assert not report.in_compliance and not report.availability_ok

    def test_latency_breach(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiEndpointSlaMonitor()
        svc.set_target("inst-1", SLATarget(endpoint_path="/api", latency_p99_ms=200))
        svc.record("inst-1", SLAMeasurement(endpoint_path="/api", timestamp=self._now(), availability_pct=100, latency_p99_ms=500, error_rate_pct=0, request_count=100))
        report = svc.check_compliance("inst-1", "/api")
        assert not report.latency_ok

    def test_no_target_passes(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiEndpointSlaMonitor()
        report = svc.check_compliance("inst-1", "/api")
        assert report.in_compliance

    def test_multiple_measurements(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiEndpointSlaMonitor()
        svc.set_target("inst-1", SLATarget(endpoint_path="/api", availability_pct=99.0))
        svc.record("inst-1", SLAMeasurement(endpoint_path="/api", timestamp=self._now(), availability_pct=100, latency_p99_ms=50, error_rate_pct=0, request_count=100))
        svc.record("inst-1", SLAMeasurement(endpoint_path="/api", timestamp=self._now(), availability_pct=98, latency_p99_ms=50, error_rate_pct=0, request_count=100))
        report = svc.check_compliance("inst-1", "/api")
        assert report.current_availability == 99.0 and report.in_compliance

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiEndpointSlaMonitor()
        svc.set_target("inst-1", SLATarget(endpoint_path="/api"))
        assert len(svc.list_targets("inst-2")) == 0
