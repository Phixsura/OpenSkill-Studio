from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_caching_v9 import fleet_api_caching_v9
def test_apic_v9():
    r = fleet_api_caching_v9([{"cached": True, "cache_hit_pct": 90, "bytes_saved_mb": 500}])
    assert r["avg_hit_rate"] == 90.0
    assert r["healthy"]
