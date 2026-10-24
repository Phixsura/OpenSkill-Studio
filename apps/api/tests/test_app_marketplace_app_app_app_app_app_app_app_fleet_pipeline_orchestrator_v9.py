from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_pipeline_orchestrator_v9 import fleet_pipeline_orchestrator_v9
def test_pipe_v9():
    r = fleet_pipeline_orchestrator_v9([{"status": "success", "duration_sec": 120}, {"status": "success", "duration_sec": 90}])
    assert r["success"] == 2
    assert r["avg_duration_sec"] == 105.0
    assert r["healthy"]
