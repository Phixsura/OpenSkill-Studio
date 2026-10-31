from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_storage_class_v9 import fleet_storage_class_v9
def test_sc3_v9():
    r = fleet_storage_class_v9([{"is_default": True, "volumes": 200, "total_gb": 5000}])
    assert r["volumes"] == 200
    assert r["healthy"]
