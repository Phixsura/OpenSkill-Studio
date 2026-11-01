from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_stripe import fleet_stripe_status
def test_stripe():
    r = fleet_stripe_status([{"active": True, "volume_24h_usd": 500000, "success_rate": 99.5}])
    assert r["volume_24h"] == 500000
    assert r["healthy"]
