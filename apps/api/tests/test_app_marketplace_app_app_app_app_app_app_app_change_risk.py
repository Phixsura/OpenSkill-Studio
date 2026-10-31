from app.services.app_marketplace_app_app_app_app_app_app_app_change_risk import assess_change_risk

def test_low_risk():
    r = assess_change_risk({"files_changed": 3, "services_affected": 1,
                               "database_migration": 0, "config_changes": 1, "rollback_complexity": 1})
    assert r["risk_level"] == "low"
    assert not r["deploy_caution"]

def test_high_risk():
    r = assess_change_risk({"files_changed": 100, "services_affected": 10,
                               "database_migration": 3, "config_changes": 20, "rollback_complexity": 5})
    assert r["risk_level"] in ("high", "critical")
    assert r["deploy_caution"]
