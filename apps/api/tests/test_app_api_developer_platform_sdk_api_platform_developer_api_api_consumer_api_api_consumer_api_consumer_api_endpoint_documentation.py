import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_endpoint_documentation import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiEndpointDocumentation, EndpointDoc, ParamDoc,
)

class TestConsumerApiEndpointDocumentation:
    def test_register_and_get(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiEndpointDocumentation()
        svc.register("inst-1", EndpointDoc(endpoint_id="e1", method="GET", path="/api/users", summary="List users", tags=["users"]))
        doc = svc.get("inst-1", "e1")
        assert doc.summary == "List users"

    def test_list_by_tag(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiEndpointDocumentation()
        svc.register("inst-1", EndpointDoc(endpoint_id="e1", method="GET", path="/api/users", summary="Users", tags=["users"]))
        svc.register("inst-1", EndpointDoc(endpoint_id="e2", method="GET", path="/api/orders", summary="Orders", tags=["orders"]))
        assert len(svc.list_by_tag("inst-1", "users")) == 1

    def test_search(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiEndpointDocumentation()
        svc.register("inst-1", EndpointDoc(endpoint_id="e1", method="POST", path="/api/auth/login", summary="Authenticate user"))
        svc.register("inst-1", EndpointDoc(endpoint_id="e2", method="GET", path="/api/users", summary="List users"))
        results = svc.search("inst-1", "auth")
        assert len(results) == 1 and results[0].endpoint_id == "e1"

    def test_exclude_deprecated(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiEndpointDocumentation()
        svc.register("inst-1", EndpointDoc(endpoint_id="e1", method="GET", path="/api/v1/old", summary="Old", deprecated=True))
        svc.register("inst-1", EndpointDoc(endpoint_id="e2", method="GET", path="/api/v2/new", summary="New"))
        assert len(svc.list_all("inst-1", include_deprecated=False)) == 1

    def test_get_tags(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiEndpointDocumentation()
        svc.register("inst-1", EndpointDoc(endpoint_id="e1", method="GET", path="/a", summary="A", tags=["auth", "users"]))
        assert svc.get_tags("inst-1") == ["auth", "users"]

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiEndpointDocumentation()
        svc.register("inst-1", EndpointDoc(endpoint_id="e1", method="GET", path="/a", summary="A"))
        assert len(svc.list_all("inst-2")) == 0
