from app.services.app_api_developer_api_endpoint_catalog import AppAPIDeveloperAPIEndpointCatalog

class TestCatalog:
    def test_register(self):
        c = AppAPIDeveloperAPIEndpointCatalog()
        ep = c.register("inst-1", "GET", "/api/users", "List users", "users")
        assert ep.auth_required is True

    def test_search(self):
        c = AppAPIDeveloperAPIEndpointCatalog()
        c.register("inst-1", "GET", "/api/users", "List users")
        c.register("inst-1", "POST", "/api/apps", "Create app")
        assert len(c.search("inst-1", "users")) == 1

    def test_stats(self):
        c = AppAPIDeveloperAPIEndpointCatalog()
        c.register("inst-1", "GET", "/api/users", "List", "users")
        c.register("inst-1", "GET", "/api/old", "Old", "legacy", deprecated=True)
        s = c.stats("inst-1")
        assert s["total"] == 2
        assert s["deprecated"] == 1

    def test_isolation(self):
        c = AppAPIDeveloperAPIEndpointCatalog()
        c.register("inst-1", "GET", "/api", "Summary")
        assert c.list_all("inst-2") == []
