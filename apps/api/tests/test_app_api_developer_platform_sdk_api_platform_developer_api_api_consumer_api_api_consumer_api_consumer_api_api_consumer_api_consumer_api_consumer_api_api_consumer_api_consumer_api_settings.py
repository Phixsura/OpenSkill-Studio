import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_api_consumer_api_consumer_api_consumer_api_api_consumer_api_consumer_api_settings import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiConsumerApiApiConsumerApiConsumerApiSettings, Setting,
)

class TestConsumerApiSettings:
    def test_set_and_get(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiConsumerApiApiConsumerApiConsumerApiSettings()
        svc.set("inst-1", "c1", Setting(key="theme", value="dark", category="display"))
        s = svc.get("inst-1", "c1", "theme")
        assert s.value == "dark"

    def test_secret_masked(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiConsumerApiApiConsumerApiConsumerApiSettings()
        svc.set("inst-1", "c1", Setting(key="api_secret", value="s3cret!", category="security", is_secret=True))
        s = svc.get("inst-1", "c1", "api_secret")
        assert s.value == "***"

    def test_get_raw(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiConsumerApiApiConsumerApiConsumerApiSettings()
        svc.set("inst-1", "c1", Setting(key="secret", value="real_value", is_secret=True))
        assert svc.get_raw("inst-1", "c1", "secret") == "real_value"

    def test_delete(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiConsumerApiApiConsumerApiConsumerApiSettings()
        svc.set("inst-1", "c1", Setting(key="temp", value="x"))
        svc.delete("inst-1", "c1", "temp")
        assert svc.get("inst-1", "c1", "temp") is None

    def test_list_by_category(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiConsumerApiApiConsumerApiConsumerApiSettings()
        svc.set("inst-1", "c1", Setting(key="a", value="1", category="security"))
        svc.set("inst-1", "c1", Setting(key="b", value="2", category="general"))
        assert len(svc.list_by_category("inst-1", "c1", category="security")) == 1

    def test_invalid_category(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiConsumerApiApiConsumerApiConsumerApiSettings()
        with pytest.raises(ValueError, match="Invalid category"):
            svc.set("inst-1", "c1", Setting(key="x", value="y", category="unknown"))

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiConsumerApiApiConsumerApiConsumerApiSettings()
        svc.set("inst-1", "c1", Setting(key="x", value="y"))
        assert svc.get("inst-2", "c1", "x") is None
