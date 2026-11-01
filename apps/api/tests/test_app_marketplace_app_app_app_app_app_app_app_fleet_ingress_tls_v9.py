from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ingress_tls_v9 import fleet_ingress_tls_v9
def test_itls_v9():
    r = fleet_ingress_tls_v9([{"tls": True, "hsts": True, "http_redirect": True}])
    assert r["tls_enabled"] == 1
    assert r["healthy"]
