from app.services.app_marketplace_app_app_app_app_app_app_app_compliance_rpt import generate_report, multi_framework

def test_report():
    r = generate_report([
        {"control": "AC-1", "status": "pass"},
        {"control": "AC-2", "status": "pass"},
        {"control": "AC-3", "status": "fail", "finding": "MFA not enforced"},
    ], framework="SOC2")
    assert r["score"] == 66.7
    assert not r["compliant"]
    assert r["failed_checks"][0]["control"] == "AC-3"

def test_multi():
    reports = [
        generate_report([{"control": "a", "status": "pass"}], "SOC2"),
        generate_report([{"control": "b", "status": "fail", "finding": "x"}], "ISO27001"),
    ]
    r = multi_framework(reports)
    assert not r["all_compliant"]
    assert r["frameworks"] == 2
