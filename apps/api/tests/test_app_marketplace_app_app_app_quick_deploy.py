from app.services.app_marketplace_app_app_app_quick_deploy import start_quick_deploy, complete_deploy

def test_start():
    r = start_quick_deploy(app_id="a1", version="2.0.0")
    assert r["deploy_id"].startswith("dep_")
    assert r["status"] == "deploying"
    assert len(r["steps"]) == 4

def test_complete_success():
    r = complete_deploy(deploy_id="dep_abc", success=True)
    assert r["status"] == "success"
    assert "🎉" in r["message"]

def test_complete_fail():
    r = complete_deploy(deploy_id="dep_abc", success=False)
    assert r["status"] == "failed"
