from app.services.app_api_developer_platform_sdk_api_developer_api_api_consumer_health_check import AppAPIDeveloperPlatformSDKApiDeveloperApiApiConsumerHealthCheck

class TestConsumerHealthCheck:
    def test_healthy(self):
        c = AppAPIDeveloperPlatformSDKApiDeveloperApiApiConsumerHealthCheck()
        h = c.update("inst-1", "c1", error_rate_pct=0.5, last_active_hours_ago=1)
        assert h.overall_health == "healthy"

    def test_critical(self):
        c = AppAPIDeveloperPlatformSDKApiDeveloperApiApiConsumerHealthCheck()
        h = c.update("inst-1", "c1", auth_healthy=False, webhook_healthy=False, error_rate_pct=15)
        assert h.overall_health == "critical"

    def test_degraded(self):
        c = AppAPIDeveloperPlatformSDKApiDeveloperApiApiConsumerHealthCheck()
        h = c.update("inst-1", "c1", webhook_healthy=False)
        assert h.overall_health == "degraded"

    def test_inactive(self):
        c = AppAPIDeveloperPlatformSDKApiDeveloperApiApiConsumerHealthCheck()
        h = c.update("inst-1", "c1", last_active_hours_ago=100)
        assert h.overall_health == "inactive"

    def test_unhealthy_list(self):
        c = AppAPIDeveloperPlatformSDKApiDeveloperApiApiConsumerHealthCheck()
        c.update("inst-1", "c1")
        c.update("inst-1", "c2", auth_healthy=False)
        assert len(c.unhealthy("inst-1")) == 1

    def test_isolation(self):
        c = AppAPIDeveloperPlatformSDKApiDeveloperApiApiConsumerHealthCheck()
        c.update("inst-1", "c1")
        assert len(c.all_checks("inst-2")) == 0
