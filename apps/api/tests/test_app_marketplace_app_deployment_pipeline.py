from app.services.app_marketplace_app_deployment_pipeline import create_pipeline, advance_stage, get_pipeline_progress

def test_create():
    p = create_pipeline(app_id="a1", version_id="v1")
    assert len(p["stages"]) == 5
    assert p["status"] == "created"

def test_advance():
    p = create_pipeline(app_id="a1", version_id="v1")
    p = advance_stage(pipeline=p)
    assert p["stages"][0]["status"] == "completed"
    assert p["current_stage"] == 1

def test_complete():
    p = create_pipeline(app_id="a1", version_id="v1", stages=["a", "b"])
    p = advance_stage(pipeline=p)
    p = advance_stage(pipeline=p)
    assert p["status"] == "completed"

def test_progress():
    p = create_pipeline(app_id="a1", version_id="v1", stages=["a", "b", "c", "d"])
    p = advance_stage(pipeline=p)
    p = advance_stage(pipeline=p)
    r = get_pipeline_progress(pipeline=p)
    assert r["pct"] == 50
