from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_tls_inspector_v9 import fleet_tls_inspector_v9
def test_tls_v9():
    r = fleet_tls_inspector_v9([{"tls_version": "1.3", "weak_cipher": False, "days_to_expiry": 200}])
    assert r["tls_1_3"] == 1
    assert r["healthy"]
