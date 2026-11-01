from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_pipe_orch import fleet_ai_pipeline_orchestrator
def test_po():
    r = fleet_ai_pipeline_orchestrator([{"active": True, "pipelines_24h": 5000, "stages": 50000, "success_pct": 98}])
    assert r["pipelines_24h"] == 5000
    assert r["reliable"]
