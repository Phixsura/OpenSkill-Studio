from app.services.app_marketplace_app_app_app_app_app_app_app_deploy_risk import score_deployment_risk

def test_high():
    r = score_deployment_risk({"env": "production", "has_migration": True,
                                "services_affected": 3, "rollback_plan": True})
    assert r["level"] == "high"
    assert "production" in r["factors"]
    assert "db_migration" in r["factors"]

def test_low():
    r = score_deployment_risk({"env": "staging", "services_affected": 1, "rollback_plan": True})
    assert r["level"] == "low"
    assert r["score"] == 0
