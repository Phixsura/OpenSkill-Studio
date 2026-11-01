from app.services.app_marketplace_app_app_app_app_app_app_app_rbac_engine import (
    get_effective_permissions, check_permission, compare_roles,
)

def test_inheritance():
    perms = get_effective_permissions("admin")
    assert "apps.view" in perms  # inherited from viewer
    assert "users.manage" in perms  # own
    assert "apps.edit" in perms  # inherited from editor

def test_check():
    assert check_permission("superadmin", "anything")["allowed"]  # wildcard
    assert check_permission("viewer", "dashboard.view")["allowed"]
    assert not check_permission("viewer", "users.manage")["allowed"]

def test_compare():
    r = compare_roles("editor", "viewer")
    assert "apps.view" in r["shared"]
    assert "apps.edit" in r["only_a"]
    assert len(r["only_b"]) == 0  # viewer is subset of editor
