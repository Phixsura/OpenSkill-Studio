"""Tests for App API Tenant Config — defaults, overrides, merge."""

from app.services.app_api_tenant_config import AppAPITenantConfig


class TestDefaults:
    def test_set_defaults(self):
        c = AppAPITenantConfig()
        d = c.set_defaults("inst-1", {"theme": "light", "lang": "en"})
        assert d["theme"] == "light"


class TestOverrides:
    def test_override(self):
        c = AppAPITenantConfig()
        c.set_defaults("inst-1", {"theme": "light", "lang": "en"})
        c.set_override("inst-1", "tenant-1", "theme", "dark")
        config = c.get_config("inst-1", "tenant-1")
        assert config["theme"] == "dark"
        assert config["lang"] == "en"

    def test_no_override(self):
        c = AppAPITenantConfig()
        c.set_defaults("inst-1", {"theme": "light"})
        config = c.get_config("inst-1", "tenant-1")
        assert config["theme"] == "light"

    def test_override_keys(self):
        c = AppAPITenantConfig()
        c.set_override("inst-1", "tenant-1", "theme", "dark")
        c.set_override("inst-1", "tenant-1", "lang", "fr")
        assert c.get_override_keys("inst-1", "tenant-1") == ["lang", "theme"]

    def test_remove(self):
        c = AppAPITenantConfig()
        c.set_defaults("inst-1", {"theme": "light"})
        c.set_override("inst-1", "tenant-1", "theme", "dark")
        c.remove_override("inst-1", "tenant-1", "theme")
        config = c.get_config("inst-1", "tenant-1")
        assert config["theme"] == "light"


class TestIsolation:
    def test_cross(self):
        c = AppAPITenantConfig()
        c.set_defaults("inst-1", {"x": "1"})
        assert c.get_config("inst-2", "t1") == {}
