from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_dep_depth import fleet_dep_depth
def test_depth():
    r = fleet_dep_depth([{"dep_depth": 3}, {"dep_depth": 7}, {"dep_depth": 2}])
    assert r["max_depth"] == 7
    assert r["too_deep"] == 1
    assert not r["manageable"]
