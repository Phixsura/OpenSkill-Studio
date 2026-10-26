from app.services.app_marketplace_extension_api_gateway_router import (
    ApiGatewayRouterService,
)
import pytest


def test_register_and_match():
    svc = ApiGatewayRouterService()
    svc.register("GET", "/api/users", "ext-1", "list_users")
    m = svc.match("GET", "/api/users")
    assert m is not None
    assert m.matched is True
    assert m.route.handler == "list_users"


def test_path_params():
    svc = ApiGatewayRouterService()
    svc.register("GET", "/api/users/{id}", "ext-1", "get_user")
    m = svc.match("GET", "/api/users/abc123")
    assert m is not None
    assert m.params["id"] == "abc123"


def test_no_match():
    svc = ApiGatewayRouterService()
    svc.register("GET", "/api/users", "ext-1", "h")
    assert svc.match("POST", "/api/users") is None
    assert svc.match("GET", "/api/items") is None


def test_priority():
    svc = ApiGatewayRouterService()
    svc.register("GET", "/api/users/{id}", "ext-1", "generic", priority=0)
    svc.register("GET", "/api/users/{id}", "ext-2", "specific", priority=10)
    m = svc.match("GET", "/api/users/123")
    assert m.route.handler == "specific"


def test_middlewares():
    svc = ApiGatewayRouterService()
    r = svc.register("POST", "/api/data", "ext-1", "create",
                     middlewares=["auth", "rate_limit", "logging"])
    assert r.middlewares == ["auth", "rate_limit", "logging"]


def test_unregister():
    svc = ApiGatewayRouterService()
    r = svc.register("GET", "/api/test", "ext-1", "h")
    assert svc.unregister(r.route_id) is True
    assert svc.match("GET", "/api/test") is None


def test_path_traversal_blocked():
    svc = ApiGatewayRouterService()
    with pytest.raises(ValueError, match="traversal"):
        svc.register("GET", "/api/../secret", "ext-1", "h")


def test_route_map():
    svc = ApiGatewayRouterService()
    svc.register("GET", "/api/a", "ext-1", "ha")
    svc.register("POST", "/api/b", "ext-2", "hb")
    rmap = svc.get_route_map()
    assert len(rmap["GET"]) == 1
    assert len(rmap["POST"]) == 1


def test_list_by_extension():
    svc = ApiGatewayRouterService()
    svc.register("GET", "/api/a", "ext-1", "h1")
    svc.register("GET", "/api/b", "ext-1", "h2")
    svc.register("GET", "/api/c", "ext-2", "h3")
    routes = svc.list_routes("ext-1")
    assert len(routes) == 2
