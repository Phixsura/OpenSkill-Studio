from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_platform_inventory_v9 import fleet_platform_inventory_v9
def test_pi2_v9():
    r = fleet_platform_inventory_v9()
    assert r["health"]["all_green"]
    assert r["health"]["dora"] == "Elite"
