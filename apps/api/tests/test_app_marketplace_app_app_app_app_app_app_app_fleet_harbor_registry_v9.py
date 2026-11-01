from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_harbor_registry_v9 import fleet_harbor_registry_v9
def test_hr2_v9():
    r = fleet_harbor_registry_v9([{"healthy": True, "projects": 50, "images": 500}])
    assert r["projects"] == 50
    assert r["all_healthy"]
