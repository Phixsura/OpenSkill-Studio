from app.services.app_marketplace_app_app_app_app_app_app_app_deploy_progress import DeployProgressTracker

def test_progress():
    dpt = DeployProgressTracker()
    dpt.start("d1", ["build", "test", "deploy", "verify"])
    r = dpt.advance("d1", "build")
    assert r["progress_pct"] == 25
    dpt.advance("d1", "test")
    dpt.advance("d1", "deploy")
    r2 = dpt.advance("d1", "verify")
    assert r2["status"] == "completed"
    assert r2["progress_pct"] == 100

def test_failure():
    dpt = DeployProgressTracker()
    dpt.start("d2", ["build", "test"])
    r = dpt.advance("d2", "build", status="failed")
    assert r["status"] == "failed"
