from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_apikey_mgmt import fleet_apikey_mgmt
def test_keys():
    r = fleet_apikey_mgmt([{"status": "active", "days_until_expiry": 10}, {"status": "expired"}, {"status": "active", "days_until_expiry": 90}])
    assert r["active"] == 2
    assert r["expiring_soon"] == 1
    assert r["needs_rotation"]
