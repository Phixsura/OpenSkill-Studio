from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_pod_resource_v9 import fleet_pod_resource_v9
def test_pr2_v9():
    r = fleet_pod_resource_v9([{"cpu_millicores": 200, "cpu_requested": 500, "mem_mb": 256, "mem_requested": 512}])
    assert r["cpu_used_m"] == 200
    assert r["healthy"]
