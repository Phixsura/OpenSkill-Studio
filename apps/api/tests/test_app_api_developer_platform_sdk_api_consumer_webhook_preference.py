import pytest
from app.services.app_api_developer_platform_sdk_api_consumer_webhook_preference import AppAPIDeveloperPlatformSDKApiConsumerWebhookPreference

class TestConsumerWebhookPreference:
    def test_set(self):
        p = AppAPIDeveloperPlatformSDKApiConsumerWebhookPreference()
        pref = p.set("inst-1", "c1", preferred_format="json", compression="gzip", batch_enabled=True)
        assert pref.compression == "gzip"
        assert pref.batch_enabled is True

    def test_invalid_format(self):
        p = AppAPIDeveloperPlatformSDKApiConsumerWebhookPreference()
        with pytest.raises(ValueError):
            p.set("inst-1", "c1", preferred_format="yaml")

    def test_default(self):
        p = AppAPIDeveloperPlatformSDKApiConsumerWebhookPreference()
        pref = p.get("inst-1", "c1")
        assert pref.preferred_format == "json"
        assert pref.compression == "none"

    def test_batch_consumers(self):
        p = AppAPIDeveloperPlatformSDKApiConsumerWebhookPreference()
        p.set("inst-1", "c1", batch_enabled=True)
        p.set("inst-1", "c2", batch_enabled=False)
        assert len(p.batch_enabled_consumers("inst-1")) == 1

    def test_format_distribution(self):
        p = AppAPIDeveloperPlatformSDKApiConsumerWebhookPreference()
        p.set("inst-1", "c1", preferred_format="json")
        p.set("inst-1", "c2", preferred_format="xml")
        p.set("inst-1", "c3", preferred_format="json")
        assert p.format_distribution("inst-1") == {"json": 2, "xml": 1}

    def test_isolation(self):
        p = AppAPIDeveloperPlatformSDKApiConsumerWebhookPreference()
        p.set("inst-1", "c1")
        assert len(p.all_preferences("inst-2")) == 0
