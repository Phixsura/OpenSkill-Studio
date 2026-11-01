import pytest
from app.services.app_api_developer_app_config import AppAPIDeveloperAppConfig

class TestConfig:
    def test_create(self):
        c = AppAPIDeveloperAppConfig()
        app = c.create("inst-1", "app-1", "My App")
        assert app.name == "My App"

    def test_settings(self):
        c = AppAPIDeveloperAppConfig()
        c.create("inst-1", "app-1", "App")
        c.set_setting("inst-1", "app-1", "theme", "dark")
        assert c.get_config("inst-1", "app-1").settings["theme"] == "dark"

    def test_flags(self):
        c = AppAPIDeveloperAppConfig()
        c.create("inst-1", "app-1", "App")
        c.set_flag("inst-1", "app-1", "beta_ui", True)
        assert c.get_config("inst-1", "app-1").feature_flags["beta_ui"] is True

    def test_isolation(self):
        c = AppAPIDeveloperAppConfig()
        c.create("inst-1", "app-1", "App")
        assert c.list_apps("inst-2") == []
