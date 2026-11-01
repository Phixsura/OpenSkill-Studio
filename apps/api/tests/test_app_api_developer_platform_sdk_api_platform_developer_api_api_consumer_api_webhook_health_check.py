from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_webhook_health_check import AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiWebhookHealthCheck

class TestWebhookHealthCheck:
    def test_healthy_after_success(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiWebhookHealthCheck()
        svc.record_check("inst-1", "c1", "https://h.com/wh", True, 200, 50)
        assert svc.is_healthy("inst-1", "c1", "https://h.com/wh") is True

    def test_unhealthy_after_failures(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiWebhookHealthCheck()
        for _ in range(3): svc.record_check("inst-1", "c1", "https://h.com/wh", False, 500)
        assert svc.is_healthy("inst-1", "c1", "https://h.com/wh") is False
        assert len(svc.unhealthy_endpoints("inst-1")) == 1

    def test_recovery(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiWebhookHealthCheck()
        for _ in range(3): svc.record_check("inst-1", "c1", "https://h.com/wh", False)
        svc.record_check("inst-1", "c1", "https://h.com/wh", True, 200)
        assert svc.is_healthy("inst-1", "c1", "https://h.com/wh") is True

    def test_availability(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiWebhookHealthCheck()
        for _ in range(9): svc.record_check("inst-1", "c1", "/wh", True)
        svc.record_check("inst-1", "c1", "/wh", False)
        assert svc.availability("inst-1", "c1", "/wh") == 90.0

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiWebhookHealthCheck()
        svc.record_check("inst-1", "c1", "/wh", True)
        assert len(svc.list_health("inst-2")) == 0
