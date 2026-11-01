from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_alert_mgr import fleet_ai_alert_manager
def test_am():
    r = fleet_ai_alert_manager([{"active": True, "alerts_24h": 200, "acked": 195, "silenced": 5, "channels": 10}])
    assert r["alerts_24h"] == 200
    assert r["responsive"]
