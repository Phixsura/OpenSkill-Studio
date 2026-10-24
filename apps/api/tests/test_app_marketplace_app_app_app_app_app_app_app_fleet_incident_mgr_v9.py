from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_incident_mgr_v9 import fleet_incident_mgr_v9
def test_inc_v9():
    r = fleet_incident_mgr_v9([{"status": "resolved", "mttr_min": 5}, {"status": "resolved", "mttr_min": 3}])
    assert r["resolved"] == 2
    assert r["open"] == 0
    assert r["healthy"]
