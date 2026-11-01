from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_lifecycle_v9 import fleet_api_lifecycle_v9
def test_al_v9():
    r = fleet_api_lifecycle_v9([{"phase": "active", "consumers": 50}])
    assert r["active"] == 1
    assert r["consumers"] == 50
    assert r["healthy"]
