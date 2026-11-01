from app.services.app_marketplace_app_app_app_app_app_app_app_platform_gw import PlatformGateway

def test_routing():
    gw = PlatformGateway()
    gw.register_route("/api/users", "user-svc", ["GET", "POST"])
    gw.add_middleware("auth")
    gw.add_middleware("rate_limit")
    r = gw.route_request("GET", "/api/users")
    assert r["status"] == 200
    assert r["service"] == "user-svc"
    assert "auth" in r["middleware_applied"]

def test_404():
    gw = PlatformGateway()
    r = gw.route_request("GET", "/missing")
    assert r["status"] == 404

def test_405():
    gw = PlatformGateway()
    gw.register_route("/api/data", "data-svc", ["GET"])
    r = gw.route_request("DELETE", "/api/data")
    assert r["status"] == 405

def test_health():
    gw = PlatformGateway()
    gw.register_route("/a", "s1")
    gw.route_request("GET", "/a")
    h = gw.health()
    assert h["status"] == "healthy"
    assert h["total_requests"] == 1
