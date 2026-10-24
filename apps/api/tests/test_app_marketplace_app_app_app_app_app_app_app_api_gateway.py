from app.services.app_marketplace_app_app_app_app_app_app_app_api_gateway import create_route, build_gateway, match_route

def test_gateway():
    routes = [
        create_route("/api/users", "user-svc:8080", ["GET", "POST"], auth_required=True, rate_limit=100),
        create_route("/api/health", "health-svc:8080", ["GET"], auth_required=False),
    ]
    g = build_gateway(routes)
    assert g["total"] == 2
    assert g["by_auth"]["public"] == 1
    assert g["rate_limited"] == 1

def test_match():
    routes = [create_route("/api/users", "svc", ["GET", "POST"])]
    g = build_gateway(routes)
    assert match_route(g, "GET", "/api/users")["matched"]
    assert not match_route(g, "DELETE", "/api/users")["matched"]
