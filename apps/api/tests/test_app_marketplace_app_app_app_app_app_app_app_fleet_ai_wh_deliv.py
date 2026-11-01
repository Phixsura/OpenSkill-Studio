from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_wh_deliv import fleet_ai_webhook_delivery
def test_wd():
    r = fleet_ai_webhook_delivery([{"active": True, "sent_24h": 1000000, "delivered": 999500, "failed": 500}])
    assert r["delivery_rate"] == 99.95
    assert r["reliable"]
