from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_cert_manager_v9 import fleet_cert_manager_v9
def test_cert_v9():
    r = fleet_cert_manager_v9([{"valid": True, "days_to_expiry": 200, "auto_renew": True}])
    assert r["valid"] == 1
    assert r["expiring_soon"] == 0
    assert r["healthy"]
