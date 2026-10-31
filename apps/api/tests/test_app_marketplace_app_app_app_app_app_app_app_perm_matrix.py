from app.services.app_marketplace_app_app_app_app_app_app_app_perm_matrix import build_permission_matrix, check_permission

def test_matrix():
    r = build_permission_matrix({"users": ["read", "write"], "billing": ["read"]})
    assert r["granted"] == 3
    assert r["total"] == 24
    assert r["coverage"] == 12

def test_check():
    g = {"users": ["read", "write"]}
    assert check_permission(g, "users", "read")
    assert not check_permission(g, "users", "delete")
    assert not check_permission(g, "invalid", "read")
