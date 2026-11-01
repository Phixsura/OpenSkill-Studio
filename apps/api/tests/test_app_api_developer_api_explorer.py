from app.services.app_api_developer_api_explorer import AppAPIDeveloperAPIExplorer

class TestExplorer:
    def test_register(self):
        e = AppAPIDeveloperAPIExplorer()
        ep = e.register("inst-1", "GET", "/api/users", "List users", "users")
        assert ep.try_it_enabled is True

    def test_categories(self):
        e = AppAPIDeveloperAPIExplorer()
        e.register("inst-1", "GET", "/api/users", "List", "users")
        e.register("inst-1", "POST", "/api/apps", "Create", "apps")
        assert e.categories("inst-1") == ["apps", "users"]

    def test_search(self):
        e = AppAPIDeveloperAPIExplorer()
        e.register("inst-1", "GET", "/api/users", "List users")
        e.register("inst-1", "POST", "/api/apps", "Create app")
        assert len(e.search("inst-1", "users")) == 1

    def test_isolation(self):
        e = AppAPIDeveloperAPIExplorer()
        e.register("inst-1", "GET", "/api", "Summary")
        assert e.list_endpoints("inst-2") == []
