from app.services.app_marketplace_extension_rbac_engine import RbacEngineService


def test_basic_permission():
    svc = RbacEngineService()
    svc.create_role("viewer", "Viewer")
    svc.add_permission("viewer", "posts", "read")
    svc.assign_role("user-1", "viewer")
    assert svc.check("user-1", "posts", "read") is True
    assert svc.check("user-1", "posts", "write") is False


def test_role_hierarchy():
    svc = RbacEngineService()
    svc.create_role("viewer", "Viewer")
    svc.add_permission("viewer", "posts", "read")
    svc.create_role("editor", "Editor", inherits=["viewer"])
    svc.add_permission("editor", "posts", "write")
    svc.create_role("admin", "Admin", inherits=["editor"])
    svc.add_permission("admin", "posts", "delete")

    svc.assign_role("admin-user", "admin")
    assert svc.check("admin-user", "posts", "read") is True    # inherited from viewer
    assert svc.check("admin-user", "posts", "write") is True   # inherited from editor
    assert svc.check("admin-user", "posts", "delete") is True  # own permission


def test_deny_overrides_allow():
    svc = RbacEngineService()
    svc.create_role("user", "User")
    svc.add_permission("user", "settings", "read")
    svc.create_role("restricted", "Restricted")
    svc.add_permission("restricted", "settings", "read", effect="deny")
    svc.assign_role("user-1", "user")
    svc.assign_role("user-1", "restricted")
    assert svc.check("user-1", "settings", "read") is False  # deny wins


def test_wildcard_resource():
    svc = RbacEngineService()
    svc.create_role("superadmin", "Super Admin")
    svc.add_permission("superadmin", "*", "*")
    svc.assign_role("sa", "superadmin")
    assert svc.check("sa", "anything", "any_action") is True


def test_multiple_roles():
    svc = RbacEngineService()
    svc.create_role("writer", "Writer")
    svc.add_permission("writer", "posts", "write")
    svc.create_role("moderator", "Moderator")
    svc.add_permission("moderator", "comments", "delete")
    svc.assign_role("user-1", "writer")
    svc.assign_role("user-1", "moderator")
    assert svc.check("user-1", "posts", "write") is True
    assert svc.check("user-1", "comments", "delete") is True


def test_revoke_role():
    svc = RbacEngineService()
    svc.create_role("editor", "Editor")
    svc.add_permission("editor", "posts", "write")
    svc.assign_role("user-1", "editor")
    assert svc.check("user-1", "posts", "write") is True
    svc.revoke_role("user-1", "editor")
    assert svc.check("user-1", "posts", "write") is False


def test_no_roles():
    svc = RbacEngineService()
    assert svc.check("unknown-user", "posts", "read") is False


def test_invalid_parent():
    svc = RbacEngineService()
    try:
        svc.create_role("child", "Child", inherits=["nonexistent"])
        assert False
    except ValueError:
        pass


def test_circular_hierarchy():
    svc = RbacEngineService()
    svc.create_role("a", "A")
    svc.create_role("b", "B", inherits=["a"])
    # Manually create cycle (shouldn't happen in normal use)
    svc._roles["a"].inherits = ["b"]
    svc.add_permission("a", "x", "read")
    svc.assign_role("u", "a")
    # Should not infinite loop
    result = svc.check("u", "x", "read")
    assert result is True  # visited set prevents loop


def test_get_user_permissions():
    svc = RbacEngineService()
    svc.create_role("viewer", "V")
    svc.add_permission("viewer", "posts", "read")
    svc.assign_role("u1", "viewer")
    perms = svc.get_user_permissions("u1")
    assert len(perms) == 1
    assert perms[0]["resource"] == "posts"
