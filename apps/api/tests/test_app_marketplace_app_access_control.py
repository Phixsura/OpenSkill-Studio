from app.services.app_marketplace_app_access_control import check_permission, get_user_permissions, assign_role, can_perform_action

def test_owner_can_delete():
    assert check_permission(user_role="owner", permission="can_delete")

def test_viewer_cannot_edit():
    assert not check_permission(user_role="viewer", permission="can_edit")

def test_permissions_list():
    perms = get_user_permissions(user_role="admin")
    assert "can_edit" in perms
    assert "can_delete" not in perms

def test_assign():
    r = assign_role(app_id="a1", user_id="u1", role="developer", assigned_by="owner1")
    assert r["role"] == "developer"

def test_assign_invalid():
    r = assign_role(app_id="a1", user_id="u1", role="superadmin", assigned_by="o1")
    assert r["error"]

def test_can_perform():
    r = can_perform_action(user_role="developer", action="can_edit")
    assert r["allowed"]

def test_cannot_perform():
    r = can_perform_action(user_role="viewer", action="can_publish")
    assert not r["allowed"]
    assert "lacks" in r["reason"]
