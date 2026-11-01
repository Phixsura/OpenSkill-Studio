from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_inc_comm import fleet_incident_comms
def test_comms():
    r = fleet_incident_comms([{"stakeholders_notified": True, "notify_time_min": 5}, {"stakeholders_notified": True, "notify_time_min": 10}, {"stakeholders_notified": False}])
    assert r["notified"] == 2
    assert r["avg_notify_min"] == 7.5
    assert r["timely"]
