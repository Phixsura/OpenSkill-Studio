from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_resend import fleet_resend_status
def test_rs():
    r = fleet_resend_status([{"verified": True, "emails_24h": 100000, "delivery_rate": 99}])
    assert r["emails_24h"] == 100000
    assert r["all_verified"]
