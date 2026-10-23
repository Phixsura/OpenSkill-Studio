from app.services.app_marketplace_app_app_app_app_app_app_app_api_gateway import ApiGateway

def test_gateway():
    gw = ApiGateway()
    gw.add_route(path="/api/v1/users", upstream="http://users:8001", rate_limit=100)
    gw.add_route(path="/api/v1/billing", upstream="http://billing:8002", auth_required=True)
    gw.add_middleware("cors")
    gw.add_middleware("rate_limit")
    r = gw.resolve("/api/v1/users", "GET")
    assert r["matched"]
    assert r["allowed"]
    assert r["upstream"] == "http://users:8001"
    r2 = gw.resolve("/unknown")
    assert not r2["matched"]
    c = gw.config()
    assert c["total_routes"] == 2
    assert len(c["middleware"]) == 2
