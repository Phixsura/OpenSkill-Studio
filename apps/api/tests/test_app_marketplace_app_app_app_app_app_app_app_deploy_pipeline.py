from app.services.app_marketplace_app_app_app_app_app_app_app_deploy_pipeline import (
    create_pipeline, advance_pipeline, pipeline_summary,
)

def test_pipeline():
    p = create_pipeline("deploy", "abc12345", ["build", "test", "deploy"])
    r1 = advance_pipeline(p, True, 5000)
    assert r1["advanced"]
    assert r1["completed_stage"] == "build"
    advance_pipeline(p, True, 3000)
    r3 = advance_pipeline(p, True, 2000)
    assert p["status"] == "completed"
    s = pipeline_summary(p)
    assert s["progress_pct"] == 100
    assert s["total_duration_ms"] == 10000

def test_failure():
    p = create_pipeline("ci", "def67890", ["build", "test"])
    advance_pipeline(p, True)
    r = advance_pipeline(p, False)
    assert not r["advanced"]
    assert p["status"] == "failed"
