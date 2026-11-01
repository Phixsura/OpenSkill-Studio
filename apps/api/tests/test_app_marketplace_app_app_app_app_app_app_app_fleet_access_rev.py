from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_access_rev import fleet_access_review
def test_rev():
    r = fleet_access_review([{"reviewed": True}, {"reviewed": False, "excess_permissions": True}])
    assert r["reviewed"] == 1
    assert r["excess_permissions"] == 1
    assert not r["clean"]
