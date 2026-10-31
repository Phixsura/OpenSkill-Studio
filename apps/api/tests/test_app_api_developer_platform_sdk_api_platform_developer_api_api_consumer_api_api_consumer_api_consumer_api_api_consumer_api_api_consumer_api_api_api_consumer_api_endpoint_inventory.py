import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_api_consumer_api_api_consumer_api_api_api_consumer_api_endpoint_inventory import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiEndpointInventory, EndpointEntry,
)

class TestConsumerApiEndpointInventory:
    def test_register_and_get(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiEndpointInventory()
        svc.register("inst-1", EndpointEntry(endpoint_id="e1", method="GET", path="/api/users", description="List users", tags=["users"]))
        e = svc.get("inst-1", "e1")
        assert e.path == "/api/users"

    def test_search_by_query(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiEndpointInventory()
        svc.register("inst-1", EndpointEntry(endpoint_id="e1", method="GET", path="/api/users", description="List users"))
        svc.register("inst-1", EndpointEntry(endpoint_id="e2", method="POST", path="/api/orders", description="Create order"))
        results = svc.search("inst-1", query="user")
        assert len(results) == 1

    def test_search_by_tag(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiEndpointInventory()
        svc.register("inst-1", EndpointEntry(endpoint_id="e1", method="GET", path="/a", tags=["auth"]))
        svc.register("inst-1", EndpointEntry(endpoint_id="e2", method="GET", path="/b", tags=["billing"]))
        assert len(svc.search("inst-1", tag="auth")) == 1

    def test_summary(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiEndpointInventory()
        svc.register("inst-1", EndpointEntry(endpoint_id="e1", method="GET", path="/a"))
        svc.register("inst-1", EndpointEntry(endpoint_id="e2", method="POST", path="/b"))
        svc.register("inst-1", EndpointEntry(endpoint_id="e3", method="GET", path="/c", status="deprecated"))
        summary = svc.get_summary("inst-1")
        assert summary.total_endpoints == 3 and summary.by_method["GET"] == 2

    def test_invalid_method(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiEndpointInventory()
        with pytest.raises(ValueError, match="Invalid method"):
            svc.register("inst-1", EndpointEntry(endpoint_id="e1", method="HACK", path="/"))

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiEndpointInventory()
        svc.register("inst-1", EndpointEntry(endpoint_id="e1", method="GET", path="/api"))
        assert svc.get("inst-2", "e1") is None
