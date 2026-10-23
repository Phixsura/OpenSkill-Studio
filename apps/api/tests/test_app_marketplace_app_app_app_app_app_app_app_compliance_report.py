from app.services.app_marketplace_app_app_app_app_app_app_app_compliance_report import generate_compliance_report

def test_report():
    controls = [
        {"id": "AC-1", "name": "Access Control", "category": "Security", "status": "passed"},
        {"id": "AC-2", "name": "Encryption", "category": "Security", "status": "passed"},
        {"id": "DM-1", "name": "Data Mapping", "category": "Privacy", "status": "failed", "notes": "Incomplete"},
        {"id": "DM-2", "name": "Consent", "category": "Privacy", "status": "n/a"},
    ]
    r = generate_compliance_report(framework="soc2", org_name="Acme Corp",
                                     period="2026-Q3", controls=controls)
    assert r["framework"] == "SOC2"
    assert r["compliance_score"] == 67  # 2 passed / 3 applicable
    assert r["verdict"] == "non_compliant"
    assert r["passed"] == 2
    assert r["failed"] == 1
    assert len(r["sections"]) == 2

def test_compliant():
    controls = [{"id": "1", "name": "X", "status": "passed"}]
    r = generate_compliance_report(framework="gdpr", org_name="Test", period="Q3", controls=controls)
    assert r["verdict"] == "compliant"
    assert r["compliance_score"] == 100
