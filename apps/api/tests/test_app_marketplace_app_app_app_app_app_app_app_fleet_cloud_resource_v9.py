from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_cloud_resource_v9 import fleet_cloud_resource_v9
def test_cres_v9():
    r = fleet_cloud_resource_v9([{"utilization_pct": 70, "monthly_cost": 5000}])
    assert r["utilized"] == 1
    assert r["wasted"] == 0
    assert r["healthy"]
