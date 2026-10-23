from app.services.app_marketplace_app_permission_scanner import scan_permissions

def test_safe():
    r = scan_permissions(requested=["read_profile", "send_notifications"])
    assert r["safe_to_install"]
    assert r["max_risk"] == "low"
    assert r["total"] == 2

def test_dangerous():
    r = scan_permissions(requested=["read_profile", "access_billing", "admin_org"])
    assert not r["safe_to_install"]
    assert r["max_risk"] == "critical"

def test_unknown():
    r = scan_permissions(requested=["read_profile", "mystery_perm"])
    assert not r["safe_to_install"]
    assert r["max_risk"] == "unknown"
    assert not r["permissions"][1]["known"]
