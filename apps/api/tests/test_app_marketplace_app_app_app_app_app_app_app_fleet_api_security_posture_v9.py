from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_security_posture_v9 import fleet_api_security_posture_v9
def test_asp3_v9():
    r = fleet_api_security_posture_v9([{"security_score": 95, "auth_enforced": True, "tls_only": True}])
    assert r["secure"] == 1
    assert r["healthy"]
