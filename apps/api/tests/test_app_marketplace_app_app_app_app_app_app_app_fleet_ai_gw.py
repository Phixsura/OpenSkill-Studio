from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_gw import fleet_ai_gateway
def test_aigw():
    r = fleet_ai_gateway([{"active": True, "requests_24h": 1000000, "cache_hit_pct": 40, "tokens_saved_24h": 50000000}])
    assert r["requests_24h"] == 1000000
    assert r["tokens_saved"] == 50000000
