from app.services.app_marketplace_extension_acl import ExtAclService

def test_grant_and_check():
    svc = ExtAclService()
    svc.grant("ext-1", "/api/data", "user-1", ["read", "write"])
    assert svc.check("ext-1", "/api/data", "user-1", "read") is True
    assert svc.check("ext-1", "/api/data", "user-1", "delete") is False

def test_admin_grants_all():
    svc = ExtAclService()
    svc.grant("ext-1", "/settings", "user-1", ["admin"])
    assert svc.check("ext-1", "/settings", "user-1", "read") is True
    assert svc.check("ext-1", "/settings", "user-1", "delete") is True

def test_revoke():
    svc = ExtAclService()
    svc.grant("ext-1", "/api", "user-1", ["read"])
    svc.revoke("ext-1", "/api", "user-1")
    assert svc.check("ext-1", "/api", "user-1", "read") is False

def test_replace_rule():
    svc = ExtAclService()
    svc.grant("ext-1", "/api", "user-1", ["read"])
    svc.grant("ext-1", "/api", "user-1", ["read", "write"])
    assert svc.check("ext-1", "/api", "user-1", "write") is True
    assert len(svc.get_rules("ext-1")) == 1
