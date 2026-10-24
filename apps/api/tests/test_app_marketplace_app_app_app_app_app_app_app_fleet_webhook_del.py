from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_webhook_del import fleet_webhook_delivery
def test_delivery():
    r = fleet_webhook_delivery([{"delivered": 990, "failed": 10}, {"delivered": 995, "failed": 5}])
    assert r["delivered"] == 1985
    assert r["success_rate"] == 99.2
    assert r["reliable"]
