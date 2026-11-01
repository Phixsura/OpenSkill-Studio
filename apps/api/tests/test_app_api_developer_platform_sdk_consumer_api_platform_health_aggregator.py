import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_api_consumer_api_consumer_api_consumer_api_consumer_api_platform_health_aggregator import (
    AppAPIDeveloperPlatformSDKConsumerApiPlatformHealthAggregator, ConsumerHealth,
)

class TestPlatformHealthAggregator:
    def test_all_healthy(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiPlatformHealthAggregator()
        svc.update_consumer("inst-1", ConsumerHealth(consumer_id="c1", health_score=95, error_rate=0.1, avg_latency_ms=50, status="healthy"))
        svc.update_consumer("inst-1", ConsumerHealth(consumer_id="c2", health_score=90, error_rate=0.5, avg_latency_ms=80, status="healthy"))
        health = svc.aggregate("inst-1")
        assert health.overall_status == "healthy" and health.healthy_count == 2

    def test_critical_overall(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiPlatformHealthAggregator()
        svc.update_consumer("inst-1", ConsumerHealth(consumer_id="c1", health_score=95, error_rate=0.1, avg_latency_ms=50, status="healthy"))
        svc.update_consumer("inst-1", ConsumerHealth(consumer_id="c2", health_score=20, error_rate=15, avg_latency_ms=2000, status="critical"))
        health = svc.aggregate("inst-1")
        assert health.overall_status == "critical" and health.critical_count == 1

    def test_top_issues(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiPlatformHealthAggregator()
        svc.update_consumer("inst-1", ConsumerHealth(consumer_id="c1", health_score=50, error_rate=10, avg_latency_ms=800, status="degraded"))
        health = svc.aggregate("inst-1")
        assert len(health.top_issues) == 2  # high error + high latency

    def test_worst_consumers(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiPlatformHealthAggregator()
        svc.update_consumer("inst-1", ConsumerHealth(consumer_id="c1", health_score=90, error_rate=0, avg_latency_ms=50, status="healthy"))
        svc.update_consumer("inst-1", ConsumerHealth(consumer_id="c2", health_score=30, error_rate=10, avg_latency_ms=500, status="critical"))
        worst = svc.get_worst("inst-1", limit=1)
        assert worst[0].consumer_id == "c2"

    def test_empty(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiPlatformHealthAggregator()
        assert svc.aggregate("inst-1").overall_status == "healthy"

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiPlatformHealthAggregator()
        svc.update_consumer("inst-1", ConsumerHealth(consumer_id="c1", health_score=90, error_rate=0, avg_latency_ms=50, status="healthy"))
        assert svc.aggregate("inst-2").total_consumers == 0
