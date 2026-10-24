from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_dep_fresh import fleet_dep_freshness
def test_freshness():
    r = fleet_dep_freshness([{"versions_behind": 0}, {"versions_behind": 1}, {"versions_behind": 5}])
    assert r["outdated"] == 2
    assert r["critical"] == 1
    assert not r["up_to_date"]
