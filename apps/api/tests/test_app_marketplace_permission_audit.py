from app.services.app_marketplace_permission_audit import audit_permissions, build_permission_diff, check_sensitive_scopes

def test_audit():
    r = audit_permissions(installation={"id": "i1"}, granted_scopes=["read", "write", "admin"],
                           used_scopes=["read"])
    assert r["unused_scopes"] == ["admin", "write"]
    assert r["over_privileged"]

def test_audit_clean():
    r = audit_permissions(installation={"id": "i1"}, granted_scopes=["read"], used_scopes=["read"])
    assert not r["over_privileged"]

def test_diff():
    d = build_permission_diff(old_scopes=["read", "write"], new_scopes=["read", "admin"])
    assert d["added"] == ["admin"]
    assert d["removed"] == ["write"]
    assert d["has_changes"]

def test_sensitive():
    r = check_sensitive_scopes(scopes=["read", "admin", "billing"])
    assert r["has_sensitive"]
    assert "admin" in r["sensitive_scopes"]

def test_no_sensitive():
    r = check_sensitive_scopes(scopes=["read", "write"])
    assert not r["has_sensitive"]
