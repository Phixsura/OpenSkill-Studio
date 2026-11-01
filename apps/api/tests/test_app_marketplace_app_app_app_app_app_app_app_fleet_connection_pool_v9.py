from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_connection_pool_v9 import fleet_connection_pool_v9
def test_cp_v9():
    r = fleet_connection_pool_v9([{"active": 30, "idle": 20, "max": 100, "waiting": 0}])
    assert r["active"] == 30
    assert r["healthy"]
