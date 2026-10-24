from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_rq import fleet_resource_quota
def test_rq():
    r = fleet_resource_quota([{"cpu_used_pct": 50, "mem_used_pct": 60}, {"cpu_used_pct": 85, "mem_used_pct": 70}])
    assert r["over_threshold"] == 1
    assert not r["healthy"]
