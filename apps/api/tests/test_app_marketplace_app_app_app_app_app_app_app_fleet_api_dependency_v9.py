from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_dependency_v9 import fleet_api_dependency_v9
def test_adep_v9():
    r = fleet_api_dependency_v9([{"dependencies": ["auth", "users"], "circular_dep": False}])
    assert r["total_deps"] == 2
    assert r["healthy"]
