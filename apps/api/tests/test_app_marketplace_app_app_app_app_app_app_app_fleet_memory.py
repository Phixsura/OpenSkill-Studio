from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_memory import fleet_memory_utilization
def test_util():
    r = fleet_memory_utilization([{"mem_used_mb": 800, "mem_alloc_mb": 1024}, {"mem_used_mb": 900, "mem_alloc_mb": 1024}])
    assert r["used_mb"] == 1700
    assert r["pct"] == 83.0
    assert not r["pressure"]
