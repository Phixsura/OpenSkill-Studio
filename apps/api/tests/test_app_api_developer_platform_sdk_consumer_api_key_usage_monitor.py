import pytest
from datetime import datetime, timedelta
from app.services.app_api_developer_platform_sdk_consumer_api_consumer_endpoint_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_key_usage_monitor import (
    AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiKeyUsageMonitor,
)

class TestApiKeyUsageMonitor:
    def _now(self):
        return datetime(2026, 6, 1, 12, 0, 0)

    def test_record_and_snapshot(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiKeyUsageMonitor()
        svc.record("inst-1", "c1", "k1", False, 50, self._now())
        snapshot = svc.get_snapshot("inst-1", "c1", "k1", self._now())
        assert snapshot.requests_last_minute == 1 and snapshot.status == "active"

    def test_error_tracking(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiKeyUsageMonitor()
        for _ in range(5):
            svc.record("inst-1", "c1", "k1", True, 100, self._now())
        snapshot = svc.get_snapshot("inst-1", "c1", "k1", self._now())
        assert snapshot.errors_last_hour == 5

    def test_idle_status(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiKeyUsageMonitor()
        svc.record("inst-1", "c1", "k1", False, 50, self._now() - timedelta(minutes=5))
        snapshot = svc.get_snapshot("inst-1", "c1", "k1", self._now())
        assert snapshot.status == "idle"

    def test_alerts(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiKeyUsageMonitor()
        for _ in range(35):
            svc.record("inst-1", "c1", "k1", False, 50, self._now())
        alerts = svc.check_alerts("inst-1", "c1", "k1", self._now())
        assert any(a.alert_type == "high_usage" for a in alerts)

    def test_all_snapshots(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiKeyUsageMonitor()
        svc.record("inst-1", "c1", "k1", False, 50, self._now())
        svc.record("inst-1", "c1", "k2", False, 30, self._now())
        snapshots = svc.get_all_snapshots("inst-1", "c1", self._now())
        assert len(snapshots) == 2

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiKeyUsageMonitor()
        svc.record("inst-1", "c1", "k1", False, 50, self._now())
        assert len(svc.get_all_snapshots("inst-2", "c1", self._now())) == 0
