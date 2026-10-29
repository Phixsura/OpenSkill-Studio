from app.services.app_api_developer_api_api_developer_api_config_manager import AppAPIDeveloperAPIApiDeveloperApiConfigManager

class TestConfigManager:
    def test_set_get(self):
        m = AppAPIDeveloperAPIApiDeveloperApiConfigManager()
        m.set("inst-1", "rate_limit", 1000)
        assert m.get("inst-1", "rate_limit") == 1000

    def test_default(self):
        m = AppAPIDeveloperAPIApiDeveloperApiConfigManager()
        assert m.get("inst-1", "missing", "default") == "default"

    def test_delete(self):
        m = AppAPIDeveloperAPIApiDeveloperApiConfigManager()
        m.set("inst-1", "key", "value")
        assert m.delete("inst-1", "key") is True
        assert m.get("inst-1", "key") is None

    def test_version_bumps(self):
        m = AppAPIDeveloperAPIApiDeveloperApiConfigManager()
        m.set("inst-1", "a", 1)
        m.set("inst-1", "b", 2)
        assert m.version("inst-1") == 2

    def test_snapshot(self):
        m = AppAPIDeveloperAPIApiDeveloperApiConfigManager()
        m.set("inst-1", "key", "v1")
        s = m.snapshot("inst-1")
        assert s.config["key"] == "v1"
        m.set("inst-1", "key", "v2")
        assert s.config["key"] == "v1"  # snapshot is isolated

    def test_isolation(self):
        m = AppAPIDeveloperAPIApiDeveloperApiConfigManager()
        m.set("inst-1", "key", "value")
        assert m.get_all("inst-2") == {}
