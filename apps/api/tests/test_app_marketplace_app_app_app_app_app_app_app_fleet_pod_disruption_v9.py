from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_pod_disruption_v9 import fleet_pod_disruption_v9
def test_pdb_v9():
    r = fleet_pod_disruption_v9([{"compliant": True, "disruptions_today": 0, "min_available": 2}])
    assert r["compliant"] == 1
    assert r["disruptions_today"] == 0
    assert r["healthy"]
