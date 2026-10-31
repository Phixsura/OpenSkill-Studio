from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_model_notif import fleet_ai_model_notification
def test_mn():
    r = fleet_ai_model_notification([{"active": True, "notifications_24h": 50000, "channels": 10, "subscribers": 5000}])
    assert r["notifications_24h"] == 50000
    assert r["notifying"]
