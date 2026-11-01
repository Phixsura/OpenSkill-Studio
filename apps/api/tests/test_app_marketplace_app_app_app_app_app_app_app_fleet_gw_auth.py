from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_gw_auth import fleet_gw_auth
def test_auth():
    r = fleet_gw_auth([{"auth_method": "jwt"}, {"auth_method": "api_key"}, {"auth_method": "none"}])
    assert r["no_auth"] == 1
    assert not r["secure"]
