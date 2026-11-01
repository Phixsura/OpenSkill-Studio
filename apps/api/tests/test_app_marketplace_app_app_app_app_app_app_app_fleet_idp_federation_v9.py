from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_idp_federation_v9 import fleet_idp_federation_v9
def test_idp_v9():
    r = fleet_idp_federation_v9([{"connected": True, "protocol": "OIDC"}, {"connected": True, "protocol": "SAML"}])
    assert r["oidc"] == 1
    assert r["saml"] == 1
    assert r["healthy"]
