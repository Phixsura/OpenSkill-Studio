from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_resp_cache import fleet_ai_response_cache_v2
def test_rc():
    r = fleet_ai_response_cache_v2([{"active": True, "entries": 10000000, "hit_rate": 72, "tokens_saved": 50000000000}])
    assert r["hit_rate"] == 72.0
    assert r["effective"]
