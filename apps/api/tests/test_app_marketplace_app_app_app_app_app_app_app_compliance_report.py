from app.services.app_marketplace_app_app_app_app_app_app_app_compliance_report import generate_report, control_summary

def test_report():
    r = generate_report("Acme", "SOC2", [
        {"id": "CC1", "title": "Encryption", "status": "passed"},
        {"id": "CC2", "title": "Access Control", "status": "passed"},
        {"id": "CC3", "title": "Logging", "status": "failed"},
    ])
    assert r["passed"] == 2
    assert r["score"] == 67
    assert not r["compliant"]

def test_summary():
    reports = [
        generate_report("A", "SOC2", [{"status": "passed"}] * 10),
        generate_report("A", "GDPR", [{"status": "passed"}] * 8 + [{"status": "failed"}] * 2),
    ]
    s = control_summary(reports)
    assert s["reports"] == 2
    assert s["total_controls"] == 20
