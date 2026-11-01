from app.services.app_marketplace_app_app_app_app_app_app_app_workflow_eng import WorkflowEngine

def test_execute():
    we = WorkflowEngine()
    we.define("deploy", [
        {"name": "build", "fn": lambda ctx: {"artifact": "app.zip"}},
        {"name": "test", "fn": lambda ctx: {"passed": True}},
        {"name": "deploy", "fn": lambda ctx: {"deployed": True}},
    ])
    r = we.execute("deploy")
    assert r["success"]
    assert len(r["steps"]) == 3
    assert r["context"]["deployed"]

def test_failure():
    we = WorkflowEngine()
    we.define("bad", [
        {"name": "ok", "fn": lambda ctx: {}},
        {"name": "fail", "fn": lambda ctx: (_ for _ in ()).throw(ValueError("boom"))},
    ])
    r = we.execute("bad")
    assert not r["success"]
    assert r["failed_at"] == 1
