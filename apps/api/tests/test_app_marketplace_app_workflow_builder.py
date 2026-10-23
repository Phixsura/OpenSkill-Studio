from app.services.app_marketplace_app_workflow_builder import create_workflow

def test_create():
    r = create_workflow(name="On Install", trigger={"type": "event"},
        actions=[{"type": "send_email"}, {"type": "notify"}])
    assert r["workflow_id"].startswith("wf_")
    assert r["total_steps"] == 2
    assert r["status"] == "draft"

def test_invalid_trigger():
    r = create_workflow(name="X", trigger={"type": "magic"}, actions=[{"type": "notify"}])
    assert "error" in r

def test_no_actions():
    r = create_workflow(name="X", trigger={"type": "webhook"}, actions=[])
    assert "error" in r
