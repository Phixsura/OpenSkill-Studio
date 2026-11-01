from app.services.app_marketplace_app_app_app_app_app_deployment_monitor import build_deployment_monitor

def test_in_progress():
    r = build_deployment_monitor(deploy_id="dep_1", app_name="SuperApp", version="2.0.0",
                                  environment="production",
                                  phase_statuses={"build": "completed", "test": "running"})
    assert r["progress"] == 25
    assert r["current_phase"] == "test"
    assert r["overall"] == "in_progress"

def test_complete():
    statuses = {p: "completed" for p in ["build", "test", "deploy", "verify"]}
    r = build_deployment_monitor(deploy_id="d1", app_name="X", version="1.0",
                                  environment="prod", phase_statuses=statuses)
    assert r["progress"] == 100
    assert r["overall"] == "success"

def test_failed():
    r = build_deployment_monitor(deploy_id="d1", app_name="X", version="1.0",
                                  environment="prod",
                                  phase_statuses={"build": "completed", "test": "failed"})
    assert r["overall"] == "failed"
