from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_router import fleet_ai_router
def test_air():
    r = fleet_ai_router([{"active": True, "requests_24h": 5000000, "models": 10, "fallback_pct": 2}])
    assert r["requests_24h"] == 5000000
    assert r["fallback_pct"] == 2.0
