from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ver_strat import fleet_versioning_strategy
def test_strat():
    r = fleet_versioning_strategy([{"strategy": "url"}, {"strategy": "url"}, {"strategy": "header"}])
    assert r["strategies"]["url"] == 2
    assert not r["consistent"]
