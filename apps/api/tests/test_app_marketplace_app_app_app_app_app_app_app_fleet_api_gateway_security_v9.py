from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_gateway_security_v9 import fleet_api_gateway_security_v9
def test_ags_v9():
    r = fleet_api_gateway_security_v9([{"waf": True, "oauth": True, "jwt_validation": True}])
    assert r["waf"] == 1
    assert r["healthy"]
