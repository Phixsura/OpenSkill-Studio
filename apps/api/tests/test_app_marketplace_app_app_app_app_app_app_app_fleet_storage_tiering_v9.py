from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_storage_tiering_v9 import fleet_storage_tiering_v9
def test_tier_v9():
    r = fleet_storage_tiering_v9([{"tier": "hot", "size_gb": 100}, {"tier": "cold", "size_gb": 500}])
    assert r["hot_gb"] == 100
    assert r["cold_gb"] == 500
    assert r["healthy"]
