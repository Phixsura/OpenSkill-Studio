from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_health_score import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerHealthScore, HealthFactors,
)

class TestConsumerHealthScore:
    def test_healthy_consumer(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerHealthScore()
        svc.update_factors("inst-1", "c1", HealthFactors(success_rate=99.9, avg_latency_ms=50, quota_usage_pct=30, last_active_hours_ago=1))
        score = svc.compute("inst-1", "c1")
        assert score.grade == "A"
        assert score.risk_level == "low"

    def test_unhealthy_consumer(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerHealthScore()
        svc.update_factors("inst-1", "c1", HealthFactors(success_rate=50, avg_latency_ms=2000, error_spike=True, quota_usage_pct=95, last_active_hours_ago=100))
        score = svc.compute("inst-1", "c1")
        assert score.grade in ("D", "F")
        assert score.risk_level in ("high", "critical")

    def test_at_risk(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerHealthScore()
        svc.update_factors("inst-1", "c1", HealthFactors(success_rate=99, avg_latency_ms=50))
        svc.update_factors("inst-1", "c2", HealthFactors(success_rate=30, avg_latency_ms=5000, error_spike=True))
        at_risk = svc.at_risk("inst-1", 60.0)
        assert len(at_risk) >= 1

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerHealthScore()
        svc.update_factors("inst-1", "c1", HealthFactors())
        assert len(svc.list_scores("inst-2")) == 0
