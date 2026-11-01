from app.services.app_marketplace_app_app_app_app_app_app_app_deploy_dep_chk import check_deploy_deps

def test_can_deploy():
    r = check_deploy_deps("api", [
        {"name": "tests", "status": "ready", "required": True},
        {"name": "migrations", "status": "ready", "required": True},
        {"name": "docs", "status": "pending", "required": False},
    ])
    assert r["can_deploy"]
    assert r["passed"] == 2

def test_blocked():
    r = check_deploy_deps("api", [
        {"name": "tests", "status": "ready", "required": True},
        {"name": "security_scan", "status": "failed", "required": True},
    ])
    assert not r["can_deploy"]
    assert r["blocking"] == 1
