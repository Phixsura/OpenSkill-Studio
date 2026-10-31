from app.services.app_api_developer_platform_sdk_api_developer_api_api_platform_sdk_version_manager import AppAPIDeveloperPlatformSDKApiDeveloperApiApiPlatformSDKVersionManager

class TestSDKVersionManager:
    def test_register(self):
        m = AppAPIDeveloperPlatformSDKApiDeveloperApiApiPlatformSDKVersionManager()
        v = m.register("inst-1", "2.0.0", "python", "stable")
        assert v.status == "stable"

    def test_latest_stable(self):
        m = AppAPIDeveloperPlatformSDKApiDeveloperApiApiPlatformSDKVersionManager()
        m.register("inst-1", "1.0.0", "python")
        m.register("inst-1", "2.0.0", "python")
        m.register("inst-1", "3.0.0-beta", "python", "beta")
        assert m.latest_stable("inst-1", "python").version == "2.0.0"

    def test_deprecated_in_use(self):
        m = AppAPIDeveloperPlatformSDKApiDeveloperApiApiPlatformSDKVersionManager()
        v = m.register("inst-1", "1.0.0", "python", "deprecated")
        v.active_users = 50
        assert len(m.deprecated_in_use("inst-1")) == 1

    def test_by_language(self):
        m = AppAPIDeveloperPlatformSDKApiDeveloperApiApiPlatformSDKVersionManager()
        m.register("inst-1", "1.0", "python")
        m.register("inst-1", "1.0", "javascript")
        langs = m.by_language("inst-1")
        assert "python" in langs
        assert "javascript" in langs

    def test_isolation(self):
        m = AppAPIDeveloperPlatformSDKApiDeveloperApiApiPlatformSDKVersionManager()
        m.register("inst-1", "1.0", "python")
        assert len(m.all_versions("inst-2")) == 0
