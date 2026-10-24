from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_req_router import fleet_ai_request_router
def test_rr():
    r = fleet_ai_request_router([{"active": True, "routes_24h": 50000000, "strategies": ["cost", "latency", "quality"], "optimal_pct": 95}])
    assert r["routes_24h"] == 50000000
    assert r["smart"]
