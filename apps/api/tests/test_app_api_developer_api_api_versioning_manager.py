import time, pytest
from app.services.app_api_developer_api_api_versioning_manager import AppAPIDeveloperAPIApiVersioningManager

class TestVersioningManager:
    def test_register(self):
        m = AppAPIDeveloperAPIApiVersioningManager()
        v = m.register("inst-1", "v1", endpoints_count=10)
        assert v.status == "active"

    def test_deprecate(self):
        m = AppAPIDeveloperAPIApiVersioningManager()
        m.register("inst-1", "v1")
        v = m.deprecate("inst-1", "v1", time.time() + 86400 * 90)
        assert v.status == "deprecated"

    def test_sunset(self):
        m = AppAPIDeveloperAPIApiVersioningManager()
        m.register("inst-1", "v1")
        m.deprecate("inst-1", "v1", time.time() + 86400)
        v = m.sunset("inst-1", "v1")
        assert v.status == "sunset"

    def test_active_only(self):
        m = AppAPIDeveloperAPIApiVersioningManager()
        m.register("inst-1", "v1")
        m.register("inst-1", "v2")
        m.deprecate("inst-1", "v1", time.time() + 86400)
        assert len(m.active_versions("inst-1")) == 1

    def test_isolation(self):
        m = AppAPIDeveloperAPIApiVersioningManager()
        m.register("inst-1", "v1")
        assert len(m.list_versions("inst-2")) == 0
