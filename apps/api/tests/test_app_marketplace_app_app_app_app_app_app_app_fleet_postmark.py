from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_postmark import fleet_postmark_status
def test_pm():
    r = fleet_postmark_status([{"active": True, "delivered_24h": 200000, "bounce_rate": 0.5}])
    assert r["delivered_24h"] == 200000
    assert r["reliable"]
