from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_sendgrid import fleet_sendgrid_status
def test_sg():
    r = fleet_sendgrid_status([{"active": True, "emails_24h": 500000, "delivery_rate": 98.5, "bounce_rate": 1.5}])
    assert r["emails_24h"] == 500000
    assert r["healthy"]
