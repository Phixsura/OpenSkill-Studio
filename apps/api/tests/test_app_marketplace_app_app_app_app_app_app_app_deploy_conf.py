from app.services.app_marketplace_app_app_app_app_app_app_app_deploy_conf import calculate_confidence

def test_high_confidence():
    r = calculate_confidence({"tests_passing": True, "coverage_above_80": True,
        "no_critical_vulns": True, "canary_healthy": True, "rollback_tested": True,
        "monitoring_ready": True, "approval_received": True})
    assert r["confidence_score"] == 100
    assert r["risk_level"] == "low"
    assert r["deploy_recommended"]

def test_low_confidence():
    r = calculate_confidence({"tests_passing": True, "approval_received": True})
    assert r["confidence_score"] == 30
    assert r["risk_level"] == "high"
    assert not r["deploy_recommended"]
