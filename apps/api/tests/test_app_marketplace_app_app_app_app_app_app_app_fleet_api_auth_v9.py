from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_auth_v9 import fleet_api_auth_v9
def test_aauth_v9():
    r = fleet_api_auth_v9([{"auth": "jwt"}, {"auth": "oauth2"}])
    assert r["jwt"] == 1
    assert r["public"] == 0
    assert r["healthy"]
