from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ssl_cert_monitor_v9 import fleet_ssl_cert_monitor_v9
def test_ssl_v9():
    r = fleet_ssl_cert_monitor_v9([{"valid": True, "days_to_expiry": 200, "auto_renew": True}])
    assert r["expiring_30d"] == 0
    assert r["healthy"]
