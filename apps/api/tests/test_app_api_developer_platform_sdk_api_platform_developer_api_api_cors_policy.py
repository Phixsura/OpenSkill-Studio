import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_cors_policy import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiCorsPolicy, CorsPolicy,
)

class TestApiCorsPolicy:
    def test_allowed_origin(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiCorsPolicy()
        svc.set_policy("inst-1", CorsPolicy(policy_id="p1", endpoint="/api", allowed_origins=["https://example.com"]))
        headers = svc.check_origin("inst-1", "/api", "https://example.com")
        assert headers["Access-Control-Allow-Origin"] == "https://example.com"

    def test_blocked_origin(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiCorsPolicy()
        svc.set_policy("inst-1", CorsPolicy(policy_id="p1", endpoint="/api", allowed_origins=["https://example.com"]))
        headers = svc.check_origin("inst-1", "/api", "https://evil.com")
        assert headers == {}

    def test_wildcard_with_credentials_rejected(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiCorsPolicy()
        with pytest.raises(ValueError, match="wildcard"):
            svc.set_policy("inst-1", CorsPolicy(policy_id="p1", endpoint="/api", allowed_origins=["*"], allow_credentials=True))

    def test_credentials_header(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiCorsPolicy()
        svc.set_policy("inst-1", CorsPolicy(policy_id="p1", endpoint="/api", allowed_origins=["https://app.com"], allow_credentials=True))
        headers = svc.check_origin("inst-1", "/api", "https://app.com")
        assert headers.get("Access-Control-Allow-Credentials") == "true"

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiCorsPolicy()
        svc.set_policy("inst-1", CorsPolicy(policy_id="p1", endpoint="/api", allowed_origins=["*"]))
        assert len(svc.list_policies("inst-2")) == 0
