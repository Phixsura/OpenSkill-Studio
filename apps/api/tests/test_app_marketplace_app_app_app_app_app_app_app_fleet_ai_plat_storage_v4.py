from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_plat_storage_v4 import fleet_ai_storage_v4
def test_sv4():
    r = fleet_ai_storage_v4([{"active": True, "total_pb": 100, "used_pb": 60, "iops": 10000000}])
    assert r["available"]
