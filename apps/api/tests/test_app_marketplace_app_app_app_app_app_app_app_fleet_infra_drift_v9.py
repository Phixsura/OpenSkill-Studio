from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_infra_drift_v9 import fleet_infra_drift_v9
def test_id2_v9():
    r = fleet_infra_drift_v9([{"drifted": False, "auto_remediated": False, "resources": 100}])
    assert r["drifted"] == 0
    assert r["healthy"]
