"""Tests for Consumer API Gateway Config service."""
import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_gateway_config import (
    GatewayConfig, Route, Middleware,
)


class TestGatewayConfig:
    def test_add_and_resolve(self):
        svc = GatewayConfig()
        svc.add_route(Route("r1", "/api/users", "http://users:8080", ["GET", "POST"]))
        result = svc.resolve("/api/users", "GET")
        assert result is not None
        assert result["target_url"] == "http://users:8080"

    def test_method_filter(self):
        svc = GatewayConfig()
        svc.add_route(Route("r1", "/api/data", "http://data:8080", ["POST"]))
        assert svc.resolve("/api/data", "GET") is None
        assert svc.resolve("/api/data", "POST") is not None

    def test_middleware_chain(self):
        svc = GatewayConfig()
        svc.add_global_middleware(Middleware("auth", "auth", order=1))
        svc.add_route(Route("r1", "/api/x", "http://x:8080",
                            middlewares=[Middleware("cache", "cache", order=10)]))
        result = svc.resolve("/api/x")
        assert result["middleware_chain"] == ["auth", "cache"]

    def test_disabled_route_skipped(self):
        svc = GatewayConfig()
        svc.add_route(Route("r1", "/api/x", "http://x:8080"))
        svc.toggle_route("r1", False)
        assert svc.resolve("/api/x") is None

    def test_toggle(self):
        svc = GatewayConfig()
        svc.add_route(Route("r1", "/api/x", "http://x:8080"))
        svc.toggle_route("r1", False)
        svc.toggle_route("r1", True)
        assert svc.resolve("/api/x") is not None

    def test_remove_route(self):
        svc = GatewayConfig()
        svc.add_route(Route("r1", "/api/x", "http://x:8080"))
        assert svc.remove_route("r1")["removed"] is True
        assert svc.resolve("/api/x") is None

    def test_prefix_match(self):
        svc = GatewayConfig()
        svc.add_route(Route("r1", "/api/users/*", "http://users:8080"))
        result = svc.resolve("/api/users/123")
        assert result is not None

    def test_list_routes(self):
        svc = GatewayConfig()
        svc.add_route(Route("r1", "/api/a", "http://a:8080"))
        svc.add_route(Route("r2", "/api/b", "http://b:8080"))
        assert len(svc.list_routes()) == 2

    def test_stats(self):
        svc = GatewayConfig()
        svc.add_route(Route("r1", "/a", "http://a:8080"))
        svc.add_route(Route("r2", "/b", "http://b:8080"))
        svc.toggle_route("r2", False)
        svc.add_global_middleware(Middleware("log", "logging"))
        stats = svc.get_stats()
        assert stats["enabled"] == 1
        assert stats["disabled"] == 1
        assert stats["global_middlewares"] == 1

    def test_duplicate_route(self):
        svc = GatewayConfig()
        svc.add_route(Route("r1", "/a", "http://a:8080"))
        with pytest.raises(ValueError):
            svc.add_route(Route("r1", "/b", "http://b:8080"))

    def test_invalid_path(self):
        svc = GatewayConfig()
        with pytest.raises(ValueError):
            svc.add_route(Route("r1", "no-slash", "http://a:8080"))

    def test_isolation(self):
        a, b = GatewayConfig(), GatewayConfig()
        a.add_route(Route("r1", "/api/x", "http://x:8080"))
        assert b.resolve("/api/x") is None
