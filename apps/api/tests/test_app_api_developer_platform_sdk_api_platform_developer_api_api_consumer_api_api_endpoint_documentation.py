from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_endpoint_documentation import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiEndpointDocumentation, EndpointDoc,
)

class TestEndpointDocumentation:
    def test_set_and_get(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiEndpointDocumentation()
        svc.set_doc("inst-1", EndpointDoc(endpoint="/users", method="GET", summary="List users", tags=["users"]))
        doc = svc.get_doc("inst-1", "GET", "/users")
        assert doc is not None and doc.summary == "List users"

    def test_search(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiEndpointDocumentation()
        svc.set_doc("inst-1", EndpointDoc(endpoint="/users", method="GET", summary="List all users"))
        svc.set_doc("inst-1", EndpointDoc(endpoint="/orders", method="POST", summary="Create order"))
        results = svc.search("inst-1", "user")
        assert len(results) == 1

    def test_by_tag(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiEndpointDocumentation()
        svc.set_doc("inst-1", EndpointDoc(endpoint="/users", method="GET", summary="List users", tags=["users", "read"]))
        svc.set_doc("inst-1", EndpointDoc(endpoint="/orders", method="POST", summary="Create order", tags=["orders"]))
        assert len(svc.by_tag("inst-1", "users")) == 1

    def test_undocumented(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiEndpointDocumentation()
        svc.set_doc("inst-1", EndpointDoc(endpoint="/users", method="GET", summary="List users"))
        count = svc.undocumented_count("inst-1", [("GET", "/users"), ("POST", "/users"), ("GET", "/orders")])
        assert count == 2

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiEndpointDocumentation()
        svc.set_doc("inst-1", EndpointDoc(endpoint="/api", method="GET", summary="X"))
        assert len(svc.list_docs("inst-2")) == 0
