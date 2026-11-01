from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_webhook_backoff import AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiWebhookBackoff
import pytest

class TestWebhookBackoff:
    def test_exponential_delay(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiWebhookBackoff()
        svc.configure("inst-1", "c1", "/hook", base_delay_s=1, multiplier=2.0)
        svc.record_failure("inst-1", "c1", "/hook")  # attempt 1 → 2s
        assert svc.get_delay("inst-1", "c1", "/hook") == 2
        svc.record_failure("inst-1", "c1", "/hook")  # attempt 2 → 4s
        assert svc.get_delay("inst-1", "c1", "/hook") == 4

    def test_max_delay_cap(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiWebhookBackoff()
        svc.configure("inst-1", "c1", "/hook", base_delay_s=100, max_delay_s=500, multiplier=2.0)
        for _ in range(10): svc.record_failure("inst-1", "c1", "/hook")
        assert svc.get_delay("inst-1", "c1", "/hook") == 500

    def test_success_resets(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiWebhookBackoff()
        svc.configure("inst-1", "c1", "/hook")
        svc.record_failure("inst-1", "c1", "/hook")
        svc.record_success("inst-1", "c1", "/hook")
        assert svc.get_delay("inst-1", "c1", "/hook") == 0

    def test_invalid_multiplier(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiWebhookBackoff()
        with pytest.raises(ValueError, match="multiplier"):
            svc.configure("inst-1", "c1", "/hook", multiplier=1.0)

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiWebhookBackoff()
        svc.configure("inst-1", "c1", "/hook")
        assert len(svc.list_states("inst-2")) == 0
