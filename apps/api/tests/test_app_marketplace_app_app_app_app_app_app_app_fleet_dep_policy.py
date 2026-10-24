from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_dep_policy import fleet_dep_update_policy
def test_policy():
    r = fleet_dep_update_policy([{"auto_update": True, "version_pinned": True}, {"auto_update": False}])
    assert r["auto_update"] == 1
    assert not r["modern"]
