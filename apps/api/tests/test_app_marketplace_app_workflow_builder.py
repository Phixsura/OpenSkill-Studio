from app.services.app_marketplace_app_workflow_builder import create_workflow, validate_workflow, execute_workflow

def test_create():
    w = create_workflow(name="Auto-assign", trigger={"event": "issue.created"},
                         actions=[{"type": "assign", "user": "bot"}])
    assert w["step_count"] == 2
    assert w["status"] == "draft"

def test_no_trigger():
    w = create_workflow(name="Bad", trigger={}, actions=[{"type": "x"}])
    assert w["error"]

def test_no_actions():
    w = create_workflow(name="Bad", trigger={"event": "x"}, actions=[])
    assert w["error"]

def test_validate():
    w = {"steps": [{"type": "trigger"}, {"type": "action"}]}
    r = validate_workflow(workflow=w)
    assert r["valid"]

def test_execute():
    w = {"name": "test", "steps": [{"type": "trigger"}, {"type": "action"}]}
    r = execute_workflow(workflow=w, context={})
    assert r["all_success"]
    assert r["steps_executed"] == 2
