from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_inc_timeline import fleet_ai_incident_timeline
def test_it():
    r = fleet_ai_incident_timeline([{"active": True, "incidents": 200, "events": 5000, "resolution_min": 15}])
    assert r["incidents"] == 200
    assert r["fast"]
