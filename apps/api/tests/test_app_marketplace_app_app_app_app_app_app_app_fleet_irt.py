from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_irt import fleet_incident_response
def test_irt():
    r = fleet_incident_response([{"ack_minutes": 5}, {"ack_minutes": 10}, {"ack_minutes": 30}])
    assert r["avg_ack_min"] == 15.0
    assert r["within_sla"] == 2
    assert r["sla_pct"] == 66.7
