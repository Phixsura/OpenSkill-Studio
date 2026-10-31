from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_webhook_secret_manager import AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiWebhookSecretManager

class TestWebhookSecretManager:
    def test_generate_and_verify(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiWebhookSecretManager()
        result = svc.generate_secret("inst-1", "c1")
        assert svc.verify("inst-1", "c1", result["secret"]) is True
        assert svc.verify("inst-1", "c1", "wrong") is False

    def test_masked_no_plaintext(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiWebhookSecretManager()
        result = svc.generate_secret("inst-1", "c1")
        masked = svc.get_masked("inst-1", "c1")
        assert masked.startswith("whsec_***")
        assert result["secret"] not in masked

    def test_rotation_increments_version(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiWebhookSecretManager()
        svc.generate_secret("inst-1", "c1")
        result2 = svc.generate_secret("inst-1", "c1")
        assert result2["version"] == 2

    def test_old_secret_invalid_after_rotation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiWebhookSecretManager()
        r1 = svc.generate_secret("inst-1", "c1")
        svc.generate_secret("inst-1", "c1")
        assert svc.verify("inst-1", "c1", r1["secret"]) is False

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiWebhookSecretManager()
        svc.generate_secret("inst-1", "c1")
        assert len(svc.list_secrets("inst-2")) == 0
