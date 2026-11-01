from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_incident_dashboard_v9 import fleet_api_incident_dashboard_v9
def test_aid2_v9():
    r = fleet_api_incident_dashboard_v9([{"status": "resolved", "resolution_min": 10}])
    assert r["resolved"] == 1
    assert r["healthy"]
