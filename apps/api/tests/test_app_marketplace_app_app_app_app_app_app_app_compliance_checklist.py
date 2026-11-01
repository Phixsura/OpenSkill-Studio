from app.services.app_marketplace_app_app_app_app_app_app_app_compliance_checklist import get_checklist, evaluate_compliance

def test_checklist():
    c = get_checklist("soc2")
    assert c["total"] == 5
    assert c["controls"][0]["control"] == "Access Control"

def test_evaluate():
    r = evaluate_compliance("soc2", ["s1", "s2", "s3"])
    assert r["completed"] == 3
    assert r["compliance_pct"] == 60
    assert r["status"] == "in_progress"
    assert not r["ready"]

def test_full_compliance():
    r = evaluate_compliance("gdpr", ["g1", "g2", "g3", "g4"])
    assert r["ready"]
    assert r["status"] == "compliant"
    assert r["compliance_pct"] == 100
