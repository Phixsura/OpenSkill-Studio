from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_platform_storage_v8 import fleet_ai_storage_v8
def test_stv8():
    r = fleet_ai_storage_v8([{"active": True, "total_eb": 10, "iops": 1000000000, "durability": 99.999999999}])
    assert r["total_eb"] == 10
    assert r["enterprise"]
