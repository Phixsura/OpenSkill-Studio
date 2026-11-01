from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_incident_tl import fleet_incident_timeline
def test_timeline():
    r = fleet_incident_timeline([{"severity": 1, "resolved": True}, {"severity": 2, "resolved": False}, {"severity": 2, "resolved": True}])
    assert r["sev1"] == 1
    assert r["open"] == 1
    assert r["resolved"] == 2
