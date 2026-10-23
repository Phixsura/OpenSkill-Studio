from app.services.app_marketplace_complete_compliance_page import build_complete_compliance_page

def test_compliant():
    p = build_complete_compliance_page(
        app={"id": "a1", "name": "App"},
        audit_results=[{"id": "c1", "passed": True, "severity": "high"}],
        compliance_score=95, frameworks=["soc2", "gdpr"],
        remediation_steps=[])
    assert p["compliant"]
    assert p["grade"] == "A"
    assert len(p["frameworks"]) == 2

def test_not_compliant():
    p = build_complete_compliance_page(
        app={"id": "a1", "name": "App"},
        audit_results=[{"id": "c1", "passed": False, "severity": "critical"}],
        compliance_score=40, frameworks=["soc2"],
        remediation_steps=[{"step": "Fix encryption"}])
    assert not p["compliant"]
    assert p["critical_issues"] == 1
