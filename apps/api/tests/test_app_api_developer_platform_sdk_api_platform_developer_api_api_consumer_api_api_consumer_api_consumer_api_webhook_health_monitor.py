import pytest
from datetime import datetime
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_webhook_health_monitor import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiWebhookHealthMonitor, HealthCheck,
)

class TestConsumerApiWebhookHealthMonitor:
    def _now(self):
        return datetime(2026, 6, 1)

    def test_healthy(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiWebhookHealthMonitor()
        for i in range(5):
            svc.record_check("inst-1", "c1", HealthCheck(check_id=f"c{i}", webhook_id="w1", status="healthy", response_time_ms=50, status_code=200, checked_at=self._now()))
        summary = svc.get_summary("inst-1", "c1", "w1")
        assert summary.status == "healthy" and summary.uptime_pct == 100

    def test_degraded(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiWebhookHealthMonitor()
        svc.record_check("inst-1", "c1", HealthCheck(check_id="c1", webhook_id="w1", status="healthy", response_time_ms=50, checked_at=self._now()))
        svc.record_check("inst-1", "c1", HealthCheck(check_id="c2", webhook_id="w1", status="degraded", response_time_ms=500, checked_at=self._now()))
        summary = svc.get_summary("inst-1", "c1", "w1")
        assert summary.status == "degraded"

    def test_down_after_consecutive(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiWebhookHealthMonitor()
        svc.record_check("inst-1", "c1", HealthCheck(check_id="c1", webhook_id="w1", status="healthy", response_time_ms=50, checked_at=self._now()))
        for i in range(3):
            svc.record_check("inst-1", "c1", HealthCheck(check_id=f"f{i}", webhook_id="w1", status="down", response_time_ms=0, error="timeout", checked_at=self._now()))
        summary = svc.get_summary("inst-1", "c1", "w1")
        assert summary.status == "down" and summary.consecutive_failures == 3

    def test_list_unhealthy(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiWebhookHealthMonitor()
        svc.record_check("inst-1", "c1", HealthCheck(check_id="c1", webhook_id="w1", status="healthy", response_time_ms=50, checked_at=self._now()))
        svc.record_check("inst-1", "c1", HealthCheck(check_id="c2", webhook_id="w2", status="down", response_time_ms=0, checked_at=self._now()))
        unhealthy = svc.list_unhealthy("inst-1", "c1")
        assert len(unhealthy) == 1 and unhealthy[0].webhook_id == "w2"

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiWebhookHealthMonitor()
        svc.record_check("inst-1", "c1", HealthCheck(check_id="c1", webhook_id="w1", status="down", response_time_ms=0, checked_at=self._now()))
        assert len(svc.list_unhealthy("inst-2", "c1")) == 0
