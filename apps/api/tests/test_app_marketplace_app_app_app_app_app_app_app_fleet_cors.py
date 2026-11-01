from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_cors import fleet_cors_audit
def test_cors():
    r = fleet_cors_audit([{"allow_origin": "*", "has_cors": True}, {"allow_origin": "example.com", "has_cors": True}])
    assert r["wildcard_origin"] == 1
    assert not r["secure"]
