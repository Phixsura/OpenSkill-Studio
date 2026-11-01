from app.services.app_marketplace_app_app_app_permissions import build_permission_request

def test_low_risk():
    r = build_permission_request(requested=["read:profile", "read:apps"])
    assert r["total"] == 2
    assert r["max_risk"] == "low"
    assert not r["requires_admin"]

def test_high_risk():
    r = build_permission_request(requested=["read:profile", "admin:org"])
    assert r["max_risk"] == "high"
    assert r["requires_admin"]
