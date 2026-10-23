from app.services.app_marketplace_app_app_app_app_app_app_app_workflow_engine import WorkflowEngine

def test_workflow():
    e = WorkflowEngine()
    wf = e.create(name="Deploy Pipeline", trigger="push_to_main", steps=[
        {"action": "run_tests"}, {"action": "build_image"}, {"action": "deploy"},
    ])
    assert wf["steps"] == 3
    r = e.execute(wf["id"])
    assert r["status"] == "success"
    assert r["steps_executed"] == 3
    wfs = e.list_workflows()
    assert wfs[0]["runs"] == 1

def test_toggle():
    e = WorkflowEngine()
    wf = e.create(name="Test", trigger="manual", steps=[{"action": "test"}])
    e.toggle(wf["id"])
    r = e.execute(wf["id"])
    assert "error" in r
