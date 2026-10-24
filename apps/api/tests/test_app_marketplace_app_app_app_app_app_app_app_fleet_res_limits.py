from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_res_limits import fleet_resource_limits
def test_limits():
    r = fleet_resource_limits([{"has_cpu_limit": True, "has_mem_limit": True}, {"has_cpu_limit": False, "has_mem_limit": False}])
    assert r["no_cpu_limit"] == 1
    assert not r["all_limited"]
