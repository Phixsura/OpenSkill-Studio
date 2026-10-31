from app.services.app_marketplace_app_developer_app_release_pipeline_v2 import create_pipeline_v2, pass_gate, fail_gate, get_pipeline_summary

def test_create():
    p = create_pipeline_v2(app_id="a1", version_id="v1", gates=[
        {"type": "test_pass", "name": "Tests"}, {"type": "security_scan", "name": "Security"}])
    assert p["total_gates"] == 2
    assert p["status"] == "created"

def test_pass():
    p = create_pipeline_v2(app_id="a1", version_id="v1", gates=[{"name": "G1"}, {"name": "G2"}])
    p = pass_gate(pipeline=p, gate_index=0, result={"ok": True})
    assert p["stages"][0]["status"] == "passed"
    assert p["current_gate"] == 1

def test_complete():
    p = create_pipeline_v2(app_id="a1", version_id="v1", gates=[{"name": "G1"}])
    p = pass_gate(pipeline=p, gate_index=0, result={})
    assert p["status"] == "completed"

def test_fail_required():
    p = create_pipeline_v2(app_id="a1", version_id="v1", gates=[{"name": "G1", "required": True}])
    p = fail_gate(pipeline=p, gate_index=0, reason="Tests failed")
    assert p["status"] == "blocked"

def test_summary():
    p = create_pipeline_v2(app_id="a1", version_id="v1", gates=[{"name": "G1"}, {"name": "G2"}, {"name": "G3"}])
    p = pass_gate(pipeline=p, gate_index=0, result={})
    s = get_pipeline_summary(pipeline=p)
    assert s["passed"] == 1
    assert s["progress_pct"] == 33
