from app.services.app_marketplace_app_marketplace_app_permissions_dialog import build_permissions_dialog

def test_dialog():
    r = build_permissions_dialog(required=["read:users", "read:projects"], optional=["webhooks:manage"])
    assert r["total"] == 3
    assert len(r["required_permissions"]) == 2
    assert not r["has_sensitive"]

def test_sensitive():
    r = build_permissions_dialog(required=["admin:org"], optional=[])
    assert r["has_sensitive"]
    assert len(r["sensitive_permissions"]) == 1
