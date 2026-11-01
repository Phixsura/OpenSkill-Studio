import pytest
from app.services.app_api_developer_api_api_gateway_config import AppAPIDeveloperAPIApiGatewayConfig

class TestGatewayConfig:
    def test_add_route(self):
        g = AppAPIDeveloperAPIApiGatewayConfig()
        r = g.add_route("inst-1", "r1", "/api/users*", "http://users:8080", ["GET", "POST"])
        assert r.auth_required is True

    def test_invalid_path(self):
        g = AppAPIDeveloperAPIApiGatewayConfig()
        with pytest.raises(ValueError):
            g.add_route("inst-1", "r1", "no-slash", "http://up")

    def test_match(self):
        g = AppAPIDeveloperAPIApiGatewayConfig()
        g.add_route("inst-1", "r1", "/api/users*", "http://users:8080", ["GET", "POST"])
        assert g.match("inst-1", "/api/users/123", "GET") is not None
        assert g.match("inst-1", "/api/orders", "GET") is None

    def test_toggle(self):
        g = AppAPIDeveloperAPIApiGatewayConfig()
        g.add_route("inst-1", "r1", "/api/v1*", "http://v1")
        g.toggle("inst-1", "r1", False)
        assert g.match("inst-1", "/api/v1/test", "GET") is None

    def test_isolation(self):
        g = AppAPIDeveloperAPIApiGatewayConfig()
        g.add_route("inst-1", "r1", "/api*", "http://up")
        assert len(g.list_routes("inst-2")) == 0
