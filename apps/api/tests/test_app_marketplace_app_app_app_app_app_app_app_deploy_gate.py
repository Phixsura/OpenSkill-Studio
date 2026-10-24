from app.services.app_marketplace_app_app_app_app_app_app_app_deploy_gate import check_gates

def test_all_pass():
    r = check_gates([
        {"name": "tests", "passed": True, "required": True},
        {"name": "security", "passed": True, "required": True},
        {"name": "load_test", "passed": False, "required": False},
    ])
    assert r["can_deploy"]
    assert r["passed"] == 2

def test_required_fail():
    r = check_gates([
        {"name": "tests", "passed": True, "required": True},
        {"name": "security", "passed": False, "required": True},
    ])
    assert not r["can_deploy"]
    assert "security" in r["failed_required"]
