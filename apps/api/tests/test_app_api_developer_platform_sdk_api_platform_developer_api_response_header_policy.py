import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_response_header_policy import AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiResponseHeaderPolicy

class TestResponseHeaderPolicy:
    def test_add_headers(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiResponseHeaderPolicy()
        svc.set_policy("inst-1", "/api", "p1", headers={"X-Request-Id": "abc", "Cache-Control": "no-store"})
        result = svc.apply_headers("inst-1", "/api", {"Content-Type": "application/json"})
        assert result["X-Request-Id"] == "abc"
        assert result["Cache-Control"] == "no-store"
        assert result["Content-Type"] == "application/json"

    def test_remove_headers(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiResponseHeaderPolicy()
        svc.set_policy("inst-1", "/api", "p1", remove_headers=["Server", "X-Powered-By"])
        result = svc.apply_headers("inst-1", "/api", {"Server": "nginx", "Content-Type": "text/html"})
        assert "Server" not in result
        assert result["Content-Type"] == "text/html"

    def test_forbidden_header(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiResponseHeaderPolicy()
        with pytest.raises(ValueError, match="forbidden"):
            svc.set_policy("inst-1", "/api", "p1", headers={"Transfer-Encoding": "chunked"})

    def test_no_policy_passthrough(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiResponseHeaderPolicy()
        original = {"Content-Type": "text/plain"}
        result = svc.apply_headers("inst-1", "/api", original)
        assert result == original

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiResponseHeaderPolicy()
        svc.set_policy("inst-1", "/api", "p1", headers={"X-Custom": "val"})
        assert len(svc.list_policies("inst-2")) == 0
