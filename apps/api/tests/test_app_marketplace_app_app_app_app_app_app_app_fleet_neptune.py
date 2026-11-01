from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_neptune import fleet_neptune_status
def test_npt():
    r = fleet_neptune_status([{"active": True, "runs": 10000, "storage_gb": 50}])
    assert r["runs"] == 10000
    assert r["all_active"]
