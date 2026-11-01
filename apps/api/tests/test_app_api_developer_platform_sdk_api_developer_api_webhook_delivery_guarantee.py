from app.services.app_api_developer_platform_sdk_api_developer_api_webhook_delivery_guarantee import AppAPIDeveloperPlatformSDKApiDeveloperApiWebhookDeliveryGuarantee

class TestDeliveryGuarantee:
    def test_configure(self):
        g = AppAPIDeveloperPlatformSDKApiDeveloperApiWebhookDeliveryGuarantee()
        dg = g.configure("inst-1", "https://a.com", "at_least_once")
        assert dg.guarantee_type == "at_least_once"

    def test_first_try_rate(self):
        g = AppAPIDeveloperPlatformSDKApiDeveloperApiWebhookDeliveryGuarantee()
        g.configure("inst-1", "https://a.com")
        for _ in range(90): g.record("inst-1", "https://a.com", first_try=True)
        for _ in range(10): g.record("inst-1", "https://a.com", first_try=False, retried=True)
        dg = g.all_guarantees("inst-1")[0]
        assert dg.first_try_rate == 90.0
        assert dg.overall_delivery_rate == 100.0

    def test_guarantee_met(self):
        g = AppAPIDeveloperPlatformSDKApiDeveloperApiWebhookDeliveryGuarantee()
        g.configure("inst-1", "https://a.com")
        for _ in range(1000): g.record("inst-1", "https://a.com", first_try=True)
        assert g.all_guarantees("inst-1")[0].guarantee_met is True

    def test_guarantee_unmet(self):
        g = AppAPIDeveloperPlatformSDKApiDeveloperApiWebhookDeliveryGuarantee()
        g.configure("inst-1", "https://a.com")
        for _ in range(90): g.record("inst-1", "https://a.com", first_try=True)
        for _ in range(10): g.record("inst-1", "https://a.com", first_try=False, failed=True)
        assert len(g.unmet_guarantees("inst-1")) == 1

    def test_isolation(self):
        g = AppAPIDeveloperPlatformSDKApiDeveloperApiWebhookDeliveryGuarantee()
        g.configure("inst-1", "https://a.com")
        assert len(g.all_guarantees("inst-2")) == 0
