from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_replica_set_v9 import fleet_replica_set_v9
def test_rs_v9():
    r = fleet_replica_set_v9([{"desired": 3, "ready": 3, "unavailable": 0}])
    assert r["ready"] == 3
    assert r["healthy"]
