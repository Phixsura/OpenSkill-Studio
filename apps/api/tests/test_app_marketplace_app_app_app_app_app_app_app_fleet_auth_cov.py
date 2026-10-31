from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_auth_cov import fleet_auth_coverage
def test_auth():
    r = fleet_auth_coverage([{"requires_auth": True}, {"requires_auth": True}, {"requires_auth": False}])
    assert r["authenticated"] == 2
    assert r["public"] == 1
    assert not r["fully_protected"]
