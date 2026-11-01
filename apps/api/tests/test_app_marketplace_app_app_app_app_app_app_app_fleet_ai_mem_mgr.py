from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_mem_mgr import fleet_ai_memory_manager
def test_mm():
    r = fleet_ai_memory_manager([{"active": True, "total_gb": 10000, "used_gb": 7500, "oom_24h": 0}])
    assert r["utilization"] == 75.0
    assert r["stable"]
