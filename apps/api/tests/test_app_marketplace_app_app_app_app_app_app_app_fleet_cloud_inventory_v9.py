from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_cloud_inventory_v9 import fleet_cloud_inventory_v9
def test_ci3_v9():
    r = fleet_cloud_inventory_v9([{"type": "vm", "region": "us-east", "tagged": True}])
    assert r["resource_types"] == 1
    assert r["healthy"]
