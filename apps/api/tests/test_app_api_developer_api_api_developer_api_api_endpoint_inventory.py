import pytest
from app.services.app_api_developer_api_api_developer_api_api_endpoint_inventory import AppAPIDeveloperAPIApiDeveloperApiApiEndpointInventory

class TestEndpointInventory:
    def test_register(self):
        i = AppAPIDeveloperAPIApiDeveloperApiApiEndpointInventory()
        e = i.register("inst-1", "e1", "GET", "/api/v1/users", "v1", tags=["users"])
        assert e.method == "GET"

    def test_search_by_path(self):
        i = AppAPIDeveloperAPIApiDeveloperApiApiEndpointInventory()
        i.register("inst-1", "e1", "GET", "/api/v1/users", "v1")
        i.register("inst-1", "e2", "GET", "/api/v1/orders", "v1")
        assert len(i.search("inst-1", path="users")) == 1

    def test_search_by_status(self):
        i = AppAPIDeveloperAPIApiDeveloperApiApiEndpointInventory()
        i.register("inst-1", "e1", "GET", "/api/v1/users", "v1", status="active")
        i.register("inst-1", "e2", "GET", "/api/v1/old", "v1", status="deprecated")
        assert len(i.search("inst-1", status="deprecated")) == 1

    def test_stats(self):
        i = AppAPIDeveloperAPIApiDeveloperApiApiEndpointInventory()
        i.register("inst-1", "e1", "GET", "/a", "v1", documented=True)
        i.register("inst-1", "e2", "POST", "/b", "v1", documented=False)
        s = i.stats("inst-1")
        assert s["total"] == 2
        assert s["documented"] == 1

    def test_isolation(self):
        i = AppAPIDeveloperAPIApiDeveloperApiApiEndpointInventory()
        i.register("inst-1", "e1", "GET", "/api", "v1")
        assert len(i.all_endpoints("inst-2")) == 0
