from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_res_quota_v2 import fleet_ai_resource_quota_v2
def test_rqv2():
    r = fleet_ai_resource_quota_v2([{"active": True, "namespaces": 50, "gpus": 500, "memory_gb": 10000}])
    assert r["gpus"] == 500
    assert r["governed"]
