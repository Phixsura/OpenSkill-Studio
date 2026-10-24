from app.services.app_marketplace_app_app_app_app_app_app_app_deploy_status import (
    create_deployment, update_step, deployment_summary,
)

def test_deployment():
    d = create_deployment("d1", "2.0", "production", ["build", "test", "deploy"])
    r = update_step(d, "build", "completed", 5000)
    assert r["progress"] == 33
    update_step(d, "test", "completed", 3000)
    update_step(d, "deploy", "completed", 2000)
    assert d["status"] == "completed"

def test_failure():
    d = create_deployment("d2", "2.1", "staging", ["build", "test"])
    update_step(d, "build", "completed")
    update_step(d, "test", "failed")
    assert d["status"] == "failed"

def test_summary():
    deployments = [{"status": "completed"}, {"status": "completed"}, {"status": "failed"}]
    r = deployment_summary(deployments)
    assert r["success_rate"] == 67
