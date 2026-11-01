import pytest
from app.services.app_api_developer_platform_sdk_api_platform_api_developer_api_response_caching_policy import AppAPIDeveloperPlatformSDKApiPlatformApiDeveloperApiResponseCachingPolicy

class TestResponseCachingPolicy:
    def test_set_policy(self):
        p = AppAPIDeveloperPlatformSDKApiPlatformApiDeveloperApiResponseCachingPolicy()
        cp = p.set_policy("inst-1", "/api/users", 3600, "public", ["Accept", "Authorization"])
        assert cp.is_cacheable is True

    def test_no_store(self):
        p = AppAPIDeveloperPlatformSDKApiPlatformApiDeveloperApiResponseCachingPolicy()
        cp = p.set_policy("inst-1", "/api/secret", 0, "no-store")
        assert cp.is_cacheable is False

    def test_generate_header(self):
        p = AppAPIDeveloperPlatformSDKApiPlatformApiDeveloperApiResponseCachingPolicy()
        p.set_policy("inst-1", "/api/users", 3600, "public", stale_while_revalidate=60)
        h = p.generate_header("inst-1", "/api/users")
        assert "max-age=3600" in h
        assert "stale-while-revalidate=60" in h

    def test_cacheable_endpoints(self):
        p = AppAPIDeveloperPlatformSDKApiPlatformApiDeveloperApiResponseCachingPolicy()
        p.set_policy("inst-1", "/a", 3600, "public")
        p.set_policy("inst-1", "/b", 0, "no-store")
        assert len(p.cacheable_endpoints("inst-1")) == 1

    def test_isolation(self):
        p = AppAPIDeveloperPlatformSDKApiPlatformApiDeveloperApiResponseCachingPolicy()
        p.set_policy("inst-1", "/api", 3600)
        assert len(p.all_policies("inst-2")) == 0
