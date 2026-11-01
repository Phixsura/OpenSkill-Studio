import pytest
from app.services.app_api_developer_platform_sdk_api_webhook_consumer_preference_manager import AppAPIDeveloperPlatformSDKApiWebhookConsumerPreferenceManager

class TestConsumerPreferenceManager:
    def test_set(self):
        m = AppAPIDeveloperPlatformSDKApiWebhookConsumerPreferenceManager()
        p = m.set("inst-1", "c1", max_retries=5, timeout_ms=10000, batch_enabled=True)
        assert p.max_retries == 5
        assert p.batch_enabled is True

    def test_invalid_retries(self):
        m = AppAPIDeveloperPlatformSDKApiWebhookConsumerPreferenceManager()
        with pytest.raises(ValueError):
            m.set("inst-1", "c1", max_retries=-1)

    def test_invalid_algorithm(self):
        m = AppAPIDeveloperPlatformSDKApiWebhookConsumerPreferenceManager()
        with pytest.raises(ValueError):
            m.set("inst-1", "c1", signature_algorithm="md5")

    def test_default(self):
        m = AppAPIDeveloperPlatformSDKApiWebhookConsumerPreferenceManager()
        p = m.get("inst-1", "c1")
        assert p.max_retries == 3
        assert p.signature_algorithm == "sha256"

    def test_with_batch(self):
        m = AppAPIDeveloperPlatformSDKApiWebhookConsumerPreferenceManager()
        m.set("inst-1", "c1", batch_enabled=True)
        m.set("inst-1", "c2", batch_enabled=False)
        assert len(m.with_batch("inst-1")) == 1

    def test_isolation(self):
        m = AppAPIDeveloperPlatformSDKApiWebhookConsumerPreferenceManager()
        m.set("inst-1", "c1")
        assert len(m.all_preferences("inst-2")) == 0
