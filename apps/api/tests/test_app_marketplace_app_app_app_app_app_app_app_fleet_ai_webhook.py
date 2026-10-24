from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_webhook import fleet_ai_webhook
def test_wh():
    r = fleet_ai_webhook([{"active": True, "delivered_24h": 1000000, "failed_24h": 0}])
    assert r["delivered_24h"] == 1000000
    assert r["reliable"]
