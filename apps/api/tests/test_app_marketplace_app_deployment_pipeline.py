from app.services.app_marketplace_app_deployment_pipeline import create_deployment, advance_deployment

def test_create():
    r = create_deployment(app_id="a1", version="2.0.0", strategy="canary", rollout_pct=25)
    assert r["deployment_id"].startswith("dep_")
    assert r["strategy"] == "canary"
    assert len(r["stages"]) == 4

def test_invalid_strategy():
    r = create_deployment(app_id="a1", version="1.0", strategy="yolo")
    assert "error" in r

def test_advance():
    dep = create_deployment(app_id="a1", version="1.0", strategy="rolling")
    r = advance_deployment(deployment=dep, stage_name="build", success=True)
    assert r["status"] == "in_progress"
    for s in ["test", "staging", "production"]:
        r = advance_deployment(deployment={**dep, "stages": r["stages"]}, stage_name=s, success=True)
    assert r["completed"]

def test_failure():
    dep = create_deployment(app_id="a1", version="1.0", strategy="rolling")
    r = advance_deployment(deployment=dep, stage_name="test", success=False)
    assert r["status"] == "failed"
