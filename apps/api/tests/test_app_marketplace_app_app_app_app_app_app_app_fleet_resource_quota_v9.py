from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_resource_quota_v9 import fleet_resource_quota_v9
def test_rq_v9():
    r = fleet_resource_quota_v9([{"cpu_used": 50, "cpu_limit": 100, "mem_used_gb": 128, "mem_limit_gb": 256}])
    assert r["cpu_used"] == 50
    assert r["healthy"]
