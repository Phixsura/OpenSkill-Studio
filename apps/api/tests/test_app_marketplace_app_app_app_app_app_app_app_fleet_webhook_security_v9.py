from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_webhook_security_v9 import fleet_webhook_security_v9
def test_ws2_v9():
    r = fleet_webhook_security_v9([{"hmac_signed": True, "tls_only": True, "ip_filter": True}])
    assert r["hmac_signed"] == 1
    assert r["healthy"]
