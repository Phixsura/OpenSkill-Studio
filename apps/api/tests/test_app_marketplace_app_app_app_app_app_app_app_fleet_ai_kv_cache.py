from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_kv_cache import fleet_ai_kv_cache
def test_kv():
    r = fleet_ai_kv_cache([{"active": True, "size_gb": 256, "hit_rate": 92, "evictions_24h": 5000}])
    assert r["size_gb"] == 256
    assert r["hot"]
