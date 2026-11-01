from app.services.app_marketplace_app_developer_app_permissions_v2 import get_permission_details, compute_risk_summary, group_by_category

def test_details():
    d = get_permission_details(scopes=["read:users", "admin:org"])
    assert d[0]["risk"] == "low"
    assert d[1]["risk"] == "critical"

def test_risk():
    r = compute_risk_summary(scopes=["read:users", "read:projects"])
    assert r["overall_risk"] == "low"
    assert not r["requires_admin_review"]

def test_critical_risk():
    r = compute_risk_summary(scopes=["admin:org"])
    assert r["overall_risk"] == "critical"
    assert r["requires_admin_review"]

def test_group():
    g = group_by_category(scopes=["read:users", "write:users", "read:projects"])
    assert len(g["users"]) == 2
    assert len(g["projects"]) == 1
