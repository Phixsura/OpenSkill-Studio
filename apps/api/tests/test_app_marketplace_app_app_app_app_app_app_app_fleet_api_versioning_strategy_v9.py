from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_versioning_strategy_v9 import fleet_api_versioning_strategy_v9
def test_avs_v9():
    r = fleet_api_versioning_strategy_v9([{"strategy": "url"}, {"strategy": "header"}])
    assert r["url"] == 1
    assert r["healthy"]
