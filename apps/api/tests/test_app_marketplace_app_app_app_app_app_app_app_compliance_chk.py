from app.services.app_marketplace_app_app_app_app_app_app_app_compliance_chk import check_compliance, audit_all

def test_partial():
    r = check_compliance("gdpr", ["consent_mechanism", "privacy_policy"])
    assert r["passed"] == 2
    assert r["total"] == 5
    assert not r["compliant"]
    assert r["compliance_pct"] == 40

def test_full():
    r = check_compliance("soc2", ["encryption_at_rest", "encryption_in_transit",
                                    "access_controls", "audit_logging", "incident_response"])
    assert r["compliant"]
    assert r["compliance_pct"] == 100

def test_audit():
    r = audit_all({"gdpr": [], "soc2": [], "hipaa": []})
    assert r["total"] == 3
    assert r["compliant"] == 0
    assert not r["overall"]
