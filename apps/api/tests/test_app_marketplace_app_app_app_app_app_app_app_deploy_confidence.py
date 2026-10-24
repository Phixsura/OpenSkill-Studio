from app.services.app_marketplace_app_app_app_app_app_app_app_deploy_confidence import score_confidence

def test_high():
    r = score_confidence({"tests_passing_pct": 100, "code_coverage_pct": 85,
                           "security_issues": 0, "canary_healthy": True,
                           "peer_reviewed": True, "rollback_plan": True})
    assert r["level"] == "high"
    assert r["score"] >= 80

def test_low():
    r = score_confidence({"tests_passing_pct": 50, "code_coverage_pct": 20,
                           "security_issues": 5, "canary_healthy": False,
                           "peer_reviewed": False, "rollback_plan": False})
    assert r["level"] == "low"
    assert r["score"] < 50
