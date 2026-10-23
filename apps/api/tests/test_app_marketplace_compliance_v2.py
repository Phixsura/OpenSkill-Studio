from app.services.app_marketplace_compliance_v2 import run_compliance_audit, get_remediation_steps

def test_full_compliance():
    all_rules = list({"data_encryption", "access_logging", "input_validation", "rate_limiting",
                       "error_handling", "privacy_policy", "data_retention", "backup_strategy"})
    r = run_compliance_audit(completed_rules=all_rules)
    assert r["score"] == 100
    assert r["compliant"]

def test_partial():
    r = run_compliance_audit(completed_rules=["data_encryption", "rate_limiting"])
    assert r["score"] == 25
    assert not r["compliant"]  # missing input_validation (critical)

def test_remediation():
    r = get_remediation_steps(failed_rules=["data_encryption", "rate_limiting"])
    assert len(r) == 2
    assert any("encryption" in s["steps"].lower() for s in r)
