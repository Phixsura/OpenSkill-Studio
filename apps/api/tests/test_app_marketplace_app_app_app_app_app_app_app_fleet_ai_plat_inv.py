from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_plat_inv import fleet_ai_platform_inventory
def test_pi():
    r = fleet_ai_platform_inventory([{"active": True, "assets": 10000, "gpus": 5000, "storage_pb": 50}])
    assert r["gpus"] == 5000
    assert r["complete"]
