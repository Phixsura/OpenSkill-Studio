from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_incident_v7 import fleet_ai_incident_v7
def test_iv7():
    r = fleet_ai_incident_v7([{"active": True, "incidents": 10, "p1": 2, "mttr_min": 5, "postmortems": 2}])
    assert r["mttr"] == 5.0
    assert r["learning"]
