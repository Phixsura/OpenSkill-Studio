from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_incident_postmortem_v9 import fleet_incident_postmortem_v9
def test_ip_v9():
    r = fleet_incident_postmortem_v9([{"completed": True, "action_items": 5, "resolved_actions": 5}])
    assert r["completed"] == 1
    assert r["healthy"]
