from app.services.app_marketplace_uninstall_flow import validate_uninstall, build_cleanup_plan, execute_uninstall

def test_valid_uninstall():
    r = validate_uninstall(installation={"status": "active", "installed_by": "u1"}, user={"id": "u1"})
    assert r["valid"]

def test_already_uninstalled():
    r = validate_uninstall(installation={"status": "uninstalled", "installed_by": "u1"}, user={"id": "u1"})
    assert not r["valid"]

def test_wrong_user():
    r = validate_uninstall(installation={"status": "active", "installed_by": "u1"}, user={"id": "u2"})
    assert not r["valid"]

def test_admin_can_uninstall():
    r = validate_uninstall(installation={"status": "active", "installed_by": "u1"}, user={"id": "u2", "is_admin": True})
    assert r["valid"]

def test_cleanup_with_webhooks():
    steps = build_cleanup_plan(installation={"has_webhooks": True})
    actions = [s["action"] for s in steps]
    assert "remove_webhooks" in actions
    assert actions[-1] == "deactivate"

def test_execute():
    r = execute_uninstall(installation={"id": "inst_1"})
    assert r["status"] == "uninstalled"
    assert r["cleanup_completed"]
