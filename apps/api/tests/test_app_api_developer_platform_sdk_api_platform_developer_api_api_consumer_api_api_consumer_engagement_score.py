from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_engagement_score import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerEngagementScore, EngagementMetrics,
)

class TestConsumerEngagementScore:
    def test_power_user(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerEngagementScore()
        svc.update_metrics("inst-1", EngagementMetrics(consumer_id="c1", requests_per_day=50, unique_endpoints_used=10, days_since_last_request=0, webhook_success_rate=99, docs_pages_viewed=10))
        s = svc.compute("inst-1", "c1")
        assert s.level == "power_user"

    def test_dormant(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerEngagementScore()
        svc.update_metrics("inst-1", EngagementMetrics(consumer_id="c1", requests_per_day=0, unique_endpoints_used=0, days_since_last_request=30))
        s = svc.compute("inst-1", "c1")
        assert s.level == "dormant"

    def test_no_metrics_is_dormant(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerEngagementScore()
        s = svc.compute("inst-1", "unknown")
        assert s.level == "dormant" and s.score == 0

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerEngagementScore()
        svc.update_metrics("inst-1", EngagementMetrics(consumer_id="c1"))
        assert len(svc.list_scores("inst-2")) == 0
