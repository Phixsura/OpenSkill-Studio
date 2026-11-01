import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_api_consumer_api_explorer import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiExplorer, ExplorerEndpoint,
)

class TestConsumerApiExplorer:
    def test_register_and_get(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiExplorer()
        svc.register("inst-1", ExplorerEndpoint(endpoint_id="e1", method="GET", path="/api/users", summary="List users", category="users"))
        ep = svc.get("inst-1", "e1")
        assert ep.summary == "List users"

    def test_search(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiExplorer()
        svc.register("inst-1", ExplorerEndpoint(endpoint_id="e1", method="GET", path="/api/users", summary="List users"))
        svc.register("inst-1", ExplorerEndpoint(endpoint_id="e2", method="POST", path="/api/orders", summary="Create order"))
        results = svc.search("inst-1", "user")
        assert len(results) == 1

    def test_categories(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiExplorer()
        svc.register("inst-1", ExplorerEndpoint(endpoint_id="e1", method="GET", path="/api/users", summary="Users", category="users"))
        svc.register("inst-1", ExplorerEndpoint(endpoint_id="e2", method="POST", path="/api/orders", summary="Orders", category="orders"))
        cats = svc.get_by_category("inst-1")
        assert len(cats) == 2 and cats[0].name == "orders"

    def test_list_all_sorted(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiExplorer()
        svc.register("inst-1", ExplorerEndpoint(endpoint_id="e1", method="GET", path="/z", summary="Z"))
        svc.register("inst-1", ExplorerEndpoint(endpoint_id="e2", method="GET", path="/a", summary="A"))
        eps = svc.list_all("inst-1")
        assert eps[0].path == "/a"

    def test_invalid_method(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiExplorer()
        with pytest.raises(ValueError, match="Invalid method"):
            svc.register("inst-1", ExplorerEndpoint(endpoint_id="e1", method="HACK", path="/", summary="X"))

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiExplorer()
        svc.register("inst-1", ExplorerEndpoint(endpoint_id="e1", method="GET", path="/api", summary="X"))
        assert len(svc.list_all("inst-2")) == 0
