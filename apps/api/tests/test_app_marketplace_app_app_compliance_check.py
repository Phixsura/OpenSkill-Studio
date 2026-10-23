from app.services.app_marketplace_app_app_compliance_check import run_compliance_check

def test_gdpr_compliant():
    results = {c: True for c in ["data_encryption", "consent_management", "right_to_delete", "data_portability", "privacy_policy"]}
    r = run_compliance_check(framework="gdpr", results=results)
    assert r["compliant"]
    assert r["score"] == 100

def test_partial():
    r = run_compliance_check(framework="soc2", results={"access_controls": True, "encryption": True})
    assert not r["compliant"]
    assert r["passed"] == 2
    assert r["failed"] == 3

def test_unknown():
    r = run_compliance_check(framework="unknown", results={})
    assert "error" in r
