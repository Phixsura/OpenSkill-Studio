from app.services.app_marketplace_app_app_app_app_app_app_app_deploy_guard import check_guards

def test_can_deploy():
    r = check_guards({"tests_pass": True, "no_critical_vulns": True, "approval": True,
                        "no_deploy_freeze": True, "performance_budget": True, "canary_healthy": True})
    assert r["can_deploy"]
    assert r["passed"] == 6

def test_blocked():
    r = check_guards({"tests_pass": True, "no_critical_vulns": False, "approval": True,
                        "no_deploy_freeze": True})
    assert not r["can_deploy"]
    assert r["blocking_failures"] == 1
