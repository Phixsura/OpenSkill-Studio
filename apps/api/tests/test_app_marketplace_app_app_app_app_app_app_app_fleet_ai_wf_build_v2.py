from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_wf_build_v2 import fleet_ai_workflow_builder_v2
def test_wbv2():
    r = fleet_ai_workflow_builder_v2([{"active": True, "workflows": 500, "nodes": 5000, "executions_24h": 50000}])
    assert r["workflows"] == 500
    assert r["productive"]
