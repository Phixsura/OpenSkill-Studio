import pytest
from app.services.app_api_developer_api_api_developer_api_api_service_registry import AppAPIDeveloperAPIApiDeveloperApiApiServiceRegistry

class TestServiceRegistry:
    def test_register(self):
        r = AppAPIDeveloperAPIApiDeveloperApiApiServiceRegistry()
        s = r.register("inst-1", "s1", "User Service", "https://users.api.com", "v1", tags=["core"])
        assert s.status == "active"

    def test_https_required(self):
        r = AppAPIDeveloperAPIApiDeveloperApiApiServiceRegistry()
        with pytest.raises(ValueError):
            r.register("inst-1", "s1", "Bad", "http://bad.com", "v1")

    def test_discover_by_tag(self):
        r = AppAPIDeveloperAPIApiDeveloperApiApiServiceRegistry()
        r.register("inst-1", "s1", "Users", "https://a.com", "v1", tags=["core"])
        r.register("inst-1", "s2", "Analytics", "https://b.com", "v1", tags=["analytics"])
        assert len(r.discover("inst-1", tag="core")) == 1

    def test_deregister(self):
        r = AppAPIDeveloperAPIApiDeveloperApiApiServiceRegistry()
        r.register("inst-1", "s1", "Svc", "https://a.com", "v1")
        r.deregister("inst-1", "s1")
        assert len(r.discover("inst-1")) == 0

    def test_stale(self):
        r = AppAPIDeveloperAPIApiDeveloperApiApiServiceRegistry()
        s = r.register("inst-1", "s1", "Svc", "https://a.com", "v1")
        s.last_heartbeat_at -= 600  # 10 min ago
        assert len(r.stale_services("inst-1")) == 1

    def test_isolation(self):
        r = AppAPIDeveloperAPIApiDeveloperApiApiServiceRegistry()
        r.register("inst-1", "s1", "Svc", "https://a.com", "v1")
        assert len(r.all_services("inst-2")) == 0
