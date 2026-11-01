from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_api_usage_dashboard import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiApiUsageDashboard, ConsumerDashboard,
)

class TestConsumerApiUsageDashboard:
    def test_update_and_get(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiApiUsageDashboard()
        svc.update("inst-1", ConsumerDashboard(consumer_id="c1", requests_today=5000, success_rate=99.5, tier="pro"))
        d = svc.get_dashboard("inst-1", "c1")
        assert d is not None and d.tier == "pro"

    def test_status(self):
        d = ConsumerDashboard(consumer_id="c1", health_score=90)
        assert d.status == "healthy"
        d2 = ConsumerDashboard(consumer_id="c2", health_score=40)
        assert d2.status == "critical"

    def test_top_consumers(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiApiUsageDashboard()
        svc.update("inst-1", ConsumerDashboard(consumer_id="c1", requests_today=100))
        svc.update("inst-1", ConsumerDashboard(consumer_id="c2", requests_today=5000))
        top = svc.top_consumers("inst-1", 1)
        assert top[0].consumer_id == "c2"

    def test_degraded(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiApiUsageDashboard()
        svc.update("inst-1", ConsumerDashboard(consumer_id="c1", health_score=95))
        svc.update("inst-1", ConsumerDashboard(consumer_id="c2", health_score=30))
        assert len(svc.degraded_consumers("inst-1")) == 1

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiApiUsageDashboard()
        svc.update("inst-1", ConsumerDashboard(consumer_id="c1"))
        assert len(svc.list_dashboards("inst-2")) == 0
