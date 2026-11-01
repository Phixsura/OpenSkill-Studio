from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_stor_tier import fleet_ai_storage_tiering
def test_st():
    r = fleet_ai_storage_tiering([{"active": True, "hot_tb": 100, "warm_tb": 500, "cold_tb": 5000, "saved_pct": 60}])
    assert r["cold_tb"] == 5000
    assert r["optimized"]
