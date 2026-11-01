from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_service_mesh_security_v9 import fleet_service_mesh_security_v9
def test_sms_v9():
    r = fleet_service_mesh_security_v9([{"mtls_enabled": True, "auth_policy": True, "peer_auth": True}])
    assert r["mtls_enabled"] == 1
    assert r["healthy"]
