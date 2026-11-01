from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_chaos_gameday_v9 import fleet_chaos_gameday_v9
def test_cg_v9():
    r = fleet_chaos_gameday_v9([{"completed": True, "findings": 5, "improvements_made": 5}])
    assert r["completed"] == 1
    assert r["healthy"]
