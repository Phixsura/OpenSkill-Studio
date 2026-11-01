from app.services.app_marketplace_app_app_app_app_app_app_app_access_ctrl import AccessControl

def test_rbac():
    ac = AccessControl()
    ac.define_role("admin", ["read", "write", "delete", "manage"])
    ac.define_role("viewer", ["read"])
    ac.assign_role("u1", "admin")
    ac.assign_role("u2", "viewer")
    assert ac.check("u1", "delete")["allowed"]
    assert ac.check("u1", "read")["granted_by"] == "admin"
    assert not ac.check("u2", "write")["allowed"]
    assert ac.check("u2", "read")["allowed"]

def test_multi_role():
    ac = AccessControl()
    ac.define_role("editor", ["read", "write"])
    ac.define_role("auditor", ["read", "audit"])
    ac.assign_role("u1", "editor")
    ac.assign_role("u1", "auditor")
    p = ac.user_permissions("u1")
    assert p["count"] == 3  # read, write, audit
    assert "audit" in p["permissions"]

def test_revoke():
    ac = AccessControl()
    ac.define_role("admin", ["all"])
    ac.assign_role("u1", "admin")
    ac.revoke_role("u1", "admin")
    assert not ac.check("u1", "all")["allowed"]

def test_stats():
    ac = AccessControl()
    ac.define_role("r1", ["a", "b"])
    ac.define_role("r2", ["c"])
    assert ac.stats()["roles"] == 2
    assert ac.stats()["total_permissions"] == 3
