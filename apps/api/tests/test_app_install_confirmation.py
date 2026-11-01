from app.services.app_install_confirmation import build_install_confirmation

def test_basic():
    c = build_install_confirmation(app={"name": "X", "developer_name": "Dev"}, permissions=["read:cohorts"], org_name="Org")
    assert c["app_name"] == "X"
    assert c["total_permissions"] == 1
    assert c["has_high_risk"] is False

def test_high_risk():
    c = build_install_confirmation(app={"name": "X"}, permissions=["read:cohorts", "write:settings", "run:background_jobs"], org_name="O")
    assert c["has_high_risk"] is True
    assert len(c["high_risk_permissions"]) == 2
