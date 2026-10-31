from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_incident_response_v9 import fleet_incident_response_v9
def test_ir_v9():
    r = fleet_incident_response_v9([{"on_call": True, "avg_ack_min": 2, "runbook_ready": True}])
    assert r["on_call"] == 1
    assert r["healthy"]
