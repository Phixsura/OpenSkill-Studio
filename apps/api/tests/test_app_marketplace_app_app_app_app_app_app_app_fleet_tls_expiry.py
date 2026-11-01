from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_tls_expiry import fleet_tls_expiry
def test_expiry():
    r = fleet_tls_expiry([{"days_left": 90}, {"days_left": 15}, {"days_left": -1}])
    assert r["expiring_soon"] == 2
    assert r["expired"] == 1
    assert not r["all_valid"]
