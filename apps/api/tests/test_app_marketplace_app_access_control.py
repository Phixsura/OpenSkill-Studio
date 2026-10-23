from app.services.app_marketplace_app_access_control import check_permission, assign_role, list_members

def test_owner_all():
    r = check_permission(role="owner", permission="anything")
    assert r["allowed"]

def test_viewer_limited():
    r = check_permission(role="viewer", permission="publish")
    assert not r["allowed"]
    r2 = check_permission(role="viewer", permission="view")
    assert r2["allowed"]

def test_assign_ok():
    r = assign_role(user_id="u5", app_id="a1", role="developer", assigner_role="owner")
    assert r["success"]

def test_assign_blocked():
    r = assign_role(user_id="u5", app_id="a1", role="admin", assigner_role="developer")
    assert not r["success"]

def test_list():
    r = list_members(app_id="a1")
    assert r["total"] == 3
