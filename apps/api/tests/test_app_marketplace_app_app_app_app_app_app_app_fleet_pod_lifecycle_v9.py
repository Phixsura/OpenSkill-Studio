from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_pod_lifecycle_v9 import fleet_pod_lifecycle_v9
def test_pl2_v9():
    r = fleet_pod_lifecycle_v9([{"phase": "Running", "restarts": 0}, {"phase": "Running", "restarts": 0}])
    assert r["running"] == 2
    assert r["failed"] == 0
    assert r["healthy"]
