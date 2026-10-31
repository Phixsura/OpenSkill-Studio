import pytest
from app.services.app_api_developer_platform_sdk_api_endpoint_cache_invalidation import AppAPIDeveloperPlatformSDKApiEndpointCacheInvalidation

class TestCacheInvalidation:
    def test_add_rule(self):
        c = AppAPIDeveloperPlatformSDKApiEndpointCacheInvalidation()
        r = c.add_rule("inst-1", "r1", "/api/users", "on_write")
        assert r.trigger == "on_write"

    def test_trigger(self):
        c = AppAPIDeveloperPlatformSDKApiEndpointCacheInvalidation()
        c.add_rule("inst-1", "r1", "/api/users", "on_write")
        triggered = c.trigger("inst-1", "/api/users", "on_write")
        assert len(triggered) == 1
        assert triggered[0].invalidations == 1

    def test_no_match(self):
        c = AppAPIDeveloperPlatformSDKApiEndpointCacheInvalidation()
        c.add_rule("inst-1", "r1", "/api/users", "on_write")
        assert len(c.trigger("inst-1", "/api/users", "on_delete")) == 0

    def test_most_triggered(self):
        c = AppAPIDeveloperPlatformSDKApiEndpointCacheInvalidation()
        c.add_rule("inst-1", "r1", "/a", "on_write")
        c.add_rule("inst-1", "r2", "/b", "on_write")
        for _ in range(5): c.trigger("inst-1", "/a", "on_write")
        for _ in range(2): c.trigger("inst-1", "/b", "on_write")
        assert c.most_triggered("inst-1", 1)[0].endpoint == "/a"

    def test_isolation(self):
        c = AppAPIDeveloperPlatformSDKApiEndpointCacheInvalidation()
        c.add_rule("inst-1", "r1", "/api", "on_write")
        assert len(c.all_rules("inst-2")) == 0
