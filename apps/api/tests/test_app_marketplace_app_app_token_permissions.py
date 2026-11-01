from app.services.app_marketplace_app_app_token_permissions import build_token_permissions

def test_basic():
    r = build_token_permissions(granted=["read:apps", "read:analytics", "write:apps"])
    assert r["granted"] == 3
    assert r["total"] == 10
    assert not r["has_admin"]

def test_admin():
    r = build_token_permissions(granted=["admin:billing"])
    assert r["has_admin"]
