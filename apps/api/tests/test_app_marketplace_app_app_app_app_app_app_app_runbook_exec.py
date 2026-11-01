from app.services.app_marketplace_app_app_app_app_app_app_app_runbook_exec import RunbookExecutor

def test_execute():
    re = RunbookExecutor()
    re.register("restart_api", [
        {"name": "drain", "action": lambda: {"drained": True}},
        {"name": "restart", "action": lambda: {"restarted": True}},
        {"name": "verify", "action": lambda: {"healthy": True}},
    ])
    r = re.execute("restart_api")
    assert r["success"]
    assert r["completed"] == 3

def test_critical_failure():
    re = RunbookExecutor()
    re.register("deploy", [
        {"name": "build", "action": lambda: {"ok": True}},
        {"name": "test", "action": lambda: (_ for _ in ()).throw(RuntimeError("tests failed")), "critical": True},
        {"name": "deploy", "action": lambda: {"ok": True}},
    ])
    r = re.execute("deploy")
    assert not r["success"]
    assert r["stopped_at"] == 1
