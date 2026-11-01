import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_api_consumer_api_consumer_api_consumer_api_api_consumer_api_consumer_api_api_consumer_api_error_response_catalog import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiErrorResponseCatalog, ErrorDefinition,
)

class TestErrorResponseCatalog:
    def test_register_and_lookup(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiErrorResponseCatalog()
        svc.register("inst-1", ErrorDefinition(error_code="AUTH_001", http_status=401, title="Invalid Token", description="The provided API token is invalid", category="auth", resolution="Check your API key"))
        result = svc.lookup("inst-1", "AUTH_001")
        assert result.found and result.definition.title == "Invalid Token"

    def test_not_found(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiErrorResponseCatalog()
        result = svc.lookup("inst-1", "MISSING")
        assert not result.found

    def test_list_by_category(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiErrorResponseCatalog()
        svc.register("inst-1", ErrorDefinition(error_code="AUTH_001", http_status=401, title="Bad Token", description="x", category="auth"))
        svc.register("inst-1", ErrorDefinition(error_code="VAL_001", http_status=422, title="Bad Input", description="y", category="validation"))
        assert len(svc.list_by_category("inst-1", category="auth")) == 1

    def test_list_by_status(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiErrorResponseCatalog()
        svc.register("inst-1", ErrorDefinition(error_code="E1", http_status=404, title="Not Found", description="x"))
        svc.register("inst-1", ErrorDefinition(error_code="E2", http_status=404, title="Also Not Found", description="y"))
        svc.register("inst-1", ErrorDefinition(error_code="E3", http_status=500, title="Server Error", description="z", category="internal"))
        assert len(svc.list_by_status("inst-1", 404)) == 2

    def test_search(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiErrorResponseCatalog()
        svc.register("inst-1", ErrorDefinition(error_code="RATE_001", http_status=429, title="Rate Limited", description="Too many requests"))
        results = svc.search("inst-1", "rate")
        assert len(results) == 1

    def test_invalid_status(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiErrorResponseCatalog()
        with pytest.raises(ValueError, match="4xx or 5xx"):
            svc.register("inst-1", ErrorDefinition(error_code="X", http_status=200, title="OK", description="x"))

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiErrorResponseCatalog()
        svc.register("inst-1", ErrorDefinition(error_code="E1", http_status=400, title="X", description="y"))
        assert not svc.lookup("inst-2", "E1").found
