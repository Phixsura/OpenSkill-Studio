from app.services.app_marketplace_app_app_app_app_app_app_app_role_mgr import get_permissions, can_perform, can_assign_role, list_roles

def test_permissions():
    assert "delete" in get_permissions("admin")
    assert "delete" not in get_permissions("editor")

def test_can_perform():
    assert can_perform("admin", "delete")
    assert not can_perform("viewer", "create")

def test_can_assign():
    assert can_assign_role("owner", "admin")
    assert not can_assign_role("editor", "admin")
    assert not can_assign_role("admin", "admin")  # same level

def test_list():
    roles = list_roles()
    assert len(roles) == 5
