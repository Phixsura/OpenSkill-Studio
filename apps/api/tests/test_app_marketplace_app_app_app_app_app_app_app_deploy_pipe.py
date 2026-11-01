from app.services.app_marketplace_app_app_app_app_app_app_app_deploy_pipe import run_pipeline, pipeline_stats

def test_success():
    r = run_pipeline([
        {"name": "build", "fn": lambda: {"artifact": "app.tar"}},
        {"name": "test", "fn": lambda: {"passed": 100}},
        {"name": "deploy", "fn": lambda: {"deployed": True}},
    ])
    assert r["success"]
    assert r["total"] == 3

def test_failure():
    r = run_pipeline([
        {"name": "build", "fn": lambda: {"ok": True}},
        {"name": "test", "fn": lambda: (_ for _ in ()).throw(RuntimeError("failed"))},
        {"name": "deploy", "fn": lambda: {"ok": True}},
    ])
    assert not r["success"]
    assert r["stages"][2]["status"] == "skipped"

def test_stats():
    r = pipeline_stats([{"success": True}, {"success": True}, {"success": False}])
    assert r["success_rate"] == 66.7
