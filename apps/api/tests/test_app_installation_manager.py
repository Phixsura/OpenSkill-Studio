from app.services.app_installation_manager import validate_upgrade, compute_rollback_info

def test_auto_upgrade():
    r = validate_upgrade(current_version="1.0", target_version="1.1",
        current_permissions=["read:cohorts"], target_permissions=["read:cohorts"])
    assert r["can_auto_upgrade"] is True
    assert r["needs_consent"] is False

def test_needs_consent():
    r = validate_upgrade(current_version="1.0", target_version="2.0",
        current_permissions=["read:cohorts"], target_permissions=["read:cohorts", "write:cohorts"])
    assert r["can_auto_upgrade"] is False
    assert r["needs_consent"] is True
    assert "write:cohorts" in r["new_permissions"]

def test_removed_perms():
    r = validate_upgrade(current_version="2.0", target_version="3.0",
        current_permissions=["read:cohorts", "write:cohorts"], target_permissions=["read:cohorts"])
    assert "write:cohorts" in r["removed_permissions"]

def test_rollback_available():
    r = compute_rollback_info(current_version="2.0", previous_version="1.0")
    assert r["can_rollback"] is True
    assert r["rollback_target"] == "1.0"

def test_no_rollback():
    r = compute_rollback_info(current_version="1.0", previous_version=None)
    assert r["can_rollback"] is False
