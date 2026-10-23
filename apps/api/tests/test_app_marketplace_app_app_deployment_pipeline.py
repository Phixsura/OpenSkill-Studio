from app.services.app_marketplace_app_app_deployment_pipeline import build_pipeline

def test_pipeline_success():
    stages = [
        {"name": "Build", "type": "build", "status": "success", "duration_s": 30},
        {"name": "Test", "type": "test", "status": "success", "duration_s": 45},
        {"name": "Deploy", "type": "deploy", "status": "success", "duration_s": 15},
    ]
    r = build_pipeline(stages=stages, pipeline_id="p1")
    assert r["overall"] == "success"
    assert r["total_duration_s"] == 90
    assert r["stage_count"] == 3

def test_pipeline_failed():
    stages = [
        {"name": "Build", "type": "build", "status": "success", "duration_s": 30},
        {"name": "Test", "type": "test", "status": "failed", "duration_s": 10},
    ]
    r = build_pipeline(stages=stages)
    assert r["overall"] == "failed"
