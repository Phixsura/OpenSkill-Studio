from app.services.app_api_endpoint_dependency import AppAPIEndpointDependency

class TestDependency:
    def test_register(self):
        d = AppAPIEndpointDependency()
        ep = d.register("inst-1", "POST", "/api/orders", ["GET /api/auth", "GET /api/products"])
        assert len(ep.depends_on) == 2

    def test_dependencies(self):
        d = AppAPIEndpointDependency()
        d.register("inst-1", "POST", "/api/orders", ["GET /api/auth"])
        assert d.dependencies_of("inst-1", "POST", "/api/orders") == ["GET /api/auth"]

    def test_dependents(self):
        d = AppAPIEndpointDependency()
        d.register("inst-1", "POST", "/api/orders", ["GET /api/auth"])
        d.register("inst-1", "POST", "/api/payments", ["GET /api/auth"])
        assert len(d.dependents_of("inst-1", "GET /api/auth")) == 2

    def test_isolation(self):
        d = AppAPIEndpointDependency()
        d.register("inst-1", "GET", "/api", [])
        assert d.list_all("inst-2") == []
