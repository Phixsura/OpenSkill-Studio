from app.services.app_marketplace_extension_app_permission_mgr import AppPermissionMgrService

def test_grant_and_check():
    svc = AppPermissionMgrService()
    svc.grant("app1", "u1", ["read:profile", "read:data"])
    assert svc.check("app1", "u1", "read:profile") is True
    assert svc.check("app1", "u1", "admin:settings") is False

def test_revoke_specific():
    svc = AppPermissionMgrService()
    svc.grant("app1", "u1", ["read:profile", "write:data"])
    svc.revoke("app1", "u1", ["write:data"])
    assert svc.check("app1", "u1", "write:data") is False
    assert svc.check("app1", "u1", "read:profile") is True

def test_revoke_all():
    svc = AppPermissionMgrService()
    svc.grant("app1", "u1", ["read:profile"])
    svc.revoke("app1", "u1")
    assert svc.check("app1", "u1", "read:profile") is False

def test_invalid_scopes():
    svc = AppPermissionMgrService()
    try:
        svc.grant("app1", "u1", ["invalid:scope"])
        assert False
    except ValueError:
        pass
