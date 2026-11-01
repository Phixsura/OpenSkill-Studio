from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_alerting_engine_v9 import fleet_alerting_engine_v9
def test_alert_v9():
    r = fleet_alerting_engine_v9([{"state": "resolved"}, {"state": "resolved"}])
    assert r["firing"] == 0
    assert r["resolved"] == 2
    assert r["healthy"]
