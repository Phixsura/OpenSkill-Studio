from app.services.app_marketplace_app_compliance_checker import run_compliance_check, get_compliance_recommendations

def test_full_compliance():
    all_ids = ["manifest_valid", "no_secrets_in_code", "https_only", "privacy_policy",
               "data_handling", "error_handling", "rate_limiting", "documentation"]
    r = run_compliance_check(app={"id": "a1"}, completed_checks=all_ids)
    assert r["compliant"]
    assert r["score"] == 100

def test_partial():
    r = run_compliance_check(app={"id": "a1"}, completed_checks=["manifest_valid", "https_only"])
    assert not r["compliant"]
    assert r["score"] == 25

def test_blocking():
    r = run_compliance_check(app={"id": "a1"}, completed_checks=["manifest_valid"])
    assert len(r["blocking_issues"]) > 0

def test_recommendations():
    results = [{"id": "x", "label": "Fix X", "category": "security", "passed": False},
               {"id": "y", "label": "Y ok", "category": "quality", "passed": True}]
    recs = get_compliance_recommendations(results=results)
    assert len(recs) == 1
    assert "Fix X" in recs[0]
