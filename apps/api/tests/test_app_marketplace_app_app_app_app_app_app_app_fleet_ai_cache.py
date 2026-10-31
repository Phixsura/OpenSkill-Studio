from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_cache import fleet_ai_cache
def test_aic():
    r = fleet_ai_cache([{"active": True, "hit_rate_pct": 40, "tokens_saved_24h": 100000000, "cost_saved_24h": 500}])
    assert r["hit_rate"] == 40.0
    assert r["tokens_saved"] == 100000000
