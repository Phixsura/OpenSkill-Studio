from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_object_storage_v9 import fleet_object_storage_v9
def test_os_v9():
    r = fleet_object_storage_v9([{"objects": 1000000, "size_tb": 5, "versioning": True}])
    assert r["total_objects"] == 1000000
    assert r["healthy"]
