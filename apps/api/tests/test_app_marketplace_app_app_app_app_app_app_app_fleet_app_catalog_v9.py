from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_app_catalog_v9 import fleet_app_catalog_v9
def test_ac2_v9():
    r = fleet_app_catalog_v9([{"env": "production", "owner": "team-a"}, {"env": "staging", "owner": "team-b"}])
    assert r["production"] == 1
    assert r["unique_owners"] == 2
    assert r["healthy"]
