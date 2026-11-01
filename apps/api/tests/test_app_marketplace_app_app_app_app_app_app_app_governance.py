from app.services.app_marketplace_app_app_app_app_app_app_app_governance import evaluate_governance

def test_compliant():
    r = evaluate_governance({p: True for p in ["naming_convention", "code_review", "testing_coverage",
                                                  "documentation", "security_scan", "license_compliance"]})
    assert r["compliant"]
    assert r["score"] == 100

def test_violations():
    r = evaluate_governance({"naming_convention": True, "security_scan": False})
    assert not r["compliant"]
    assert r["critical_violations"] == 1
    assert r["violations"] >= 4
