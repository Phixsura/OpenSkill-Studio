from app.services.app_marketplace_app_app_permission_matrix import build_permission_matrix, check_permission

def test_defaults():
    r = build_permission_matrix()
    assert r["matrix"]["viewer"]["read"]
    assert not r["matrix"]["viewer"]["write"]
    assert r["matrix"]["owner"]["billing"]

def test_override():
    r = build_permission_matrix(overrides={"viewer": {"write": True}})
    assert r["matrix"]["viewer"]["write"]

def test_check():
    assert check_permission(role="admin", action="delete")["allowed"]
    assert not check_permission(role="editor", action="delete")["allowed"]
