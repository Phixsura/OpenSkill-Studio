from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_datasets import fleet_datasets_status
def test_ds():
    r = fleet_datasets_status([{"active": True, "datasets": 500, "total_rows": 100000000}])
    assert r["datasets"] == 500
    assert r["all_active"]
