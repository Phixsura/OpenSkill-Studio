from app.services.app_marketplace_app_app_app_app_app_app_app_rollout_risk import assess_rollout_risk

def test_low():
    r = assess_rollout_risk({"lines_changed": 10, "services_affected": 1, "has_rollback_plan": True})
    assert r["risk_level"] == "low"
    assert r["risk_score"] == 0

def test_high():
    r = assess_rollout_risk({"lines_changed": 1000, "services_affected": 5,
                                "database_migration": True, "has_rollback_plan": False})
    assert r["risk_level"] in ("high", "critical")
    assert r["recommend_canary"]
    assert len(r["risk_factors"]) >= 3
