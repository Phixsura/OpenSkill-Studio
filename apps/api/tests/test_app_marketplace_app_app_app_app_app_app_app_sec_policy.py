from app.services.app_marketplace_app_app_app_app_app_app_app_sec_policy import check_compliance, risk_score

def test_compliance():
    resource = {"name": "api-server", "policy_require_mfa": True, "policy_encrypt_at_rest": False}
    r = check_compliance(resource, ["require_mfa", "encrypt_at_rest", "audit_logging"])
    assert r["violation_count"] == 2
    assert not r["compliant"]

def test_risk():
    violations = [{"severity": "critical"}, {"severity": "high"}]
    r = risk_score(violations)
    assert r["score"] == 15
    assert r["level"] == "critical"
