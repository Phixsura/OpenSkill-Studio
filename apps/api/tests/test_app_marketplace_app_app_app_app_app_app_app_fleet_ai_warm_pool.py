from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_warm_pool import fleet_ai_warm_pool
def test_wp():
    r = fleet_ai_warm_pool([{"active": True, "warm": 50, "prevented": 100000, "overhead_pct": 15}])
    assert r["warm"] == 50
    assert r["ready"]
