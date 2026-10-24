from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_twilio import fleet_twilio_status
def test_tw():
    r = fleet_twilio_status([{"active": True, "messages_24h": 100000, "calls_24h": 5000}])
    assert r["messages_24h"] == 100000
    assert r["all_active"]
