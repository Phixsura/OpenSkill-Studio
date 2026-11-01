from app.services.app_marketplace_extension_permission_boundary import PermissionBoundaryService


def test_basic_boundary():
    svc = PermissionBoundaryService()
    svc.define_boundary("developer", ["read:*", "write:code", "deploy:staging"])
    svc.assign_boundary("user-1", "developer")
    svc.grant("user-1", ["read:users", "write:code", "admin:settings"])
    effective = svc.effective_permissions("user-1")
    assert "read:users" in effective   # allowed by read:*
    assert "write:code" in effective   # exact match
    assert "admin:settings" not in effective  # blocked by boundary


def test_no_boundary_all_granted():
    svc = PermissionBoundaryService()
    svc.grant("user-1", ["admin:settings", "deploy:prod"])
    effective = svc.effective_permissions("user-1")
    assert effective == {"admin:settings", "deploy:prod"}


def test_wildcard_boundary():
    svc = PermissionBoundaryService()
    svc.define_boundary("admin", ["*"])
    svc.assign_boundary("user-1", "admin")
    svc.grant("user-1", ["anything:goes", "super:power"])
    assert svc.check("user-1", "anything:goes") is True


def test_detect_violations():
    svc = PermissionBoundaryService()
    svc.define_boundary("readonly", ["read:*"])
    svc.assign_boundary("user-1", "readonly")
    svc.grant("user-1", ["read:data", "write:data", "delete:data"])
    violations = svc.detect_violations("user-1")
    assert "write:data" in violations
    assert "delete:data" in violations
    assert "read:data" not in violations


def test_parent_child_boundary():
    svc = PermissionBoundaryService()
    svc.define_boundary("team", ["read:*", "write:*", "deploy:staging"])
    svc.define_boundary("junior", ["read:*", "write:code"], parent="team")
    svc.assign_boundary("intern", "junior")
    svc.grant("intern", ["read:logs", "write:code", "deploy:staging"])
    effective = svc.effective_permissions("intern")
    assert "read:logs" in effective
    assert "write:code" in effective
    assert "deploy:staging" not in effective  # junior boundary doesn't include it


def test_child_cant_exceed_parent():
    svc = PermissionBoundaryService()
    svc.define_boundary("limited", ["read:*"])
    try:
        svc.define_boundary("child", ["read:*", "admin:*"], parent="limited")
        assert False
    except ValueError as e:
        assert "exceeds parent" in str(e)


def test_simulate():
    svc = PermissionBoundaryService()
    svc.define_boundary("dev", ["read:*", "write:code"])
    svc.define_boundary("ops", ["read:*", "deploy:*"])
    svc.grant("user-1", ["read:data", "write:code", "deploy:prod"])
    dev_sim = svc.simulate("user-1", "dev")
    assert "write:code" in dev_sim["effective"]
    assert "deploy:prod" in dev_sim["blocked"]
    ops_sim = svc.simulate("user-1", "ops")
    assert "deploy:prod" in ops_sim["effective"]
    assert "write:code" in ops_sim["blocked"]


def test_prefix_wildcard():
    svc = PermissionBoundaryService()
    svc.define_boundary("b", ["read:*"])
    svc.assign_boundary("u", "b")
    svc.grant("u", ["read:users", "read:logs", "read:analytics"])
    assert svc.effective_permissions("u") == {"read:users", "read:logs", "read:analytics"}


def test_check():
    svc = PermissionBoundaryService()
    svc.define_boundary("b", ["read:data"])
    svc.assign_boundary("u", "b")
    svc.grant("u", ["read:data", "write:data"])
    assert svc.check("u", "read:data") is True
    assert svc.check("u", "write:data") is False
