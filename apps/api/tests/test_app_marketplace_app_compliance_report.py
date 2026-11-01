from app.services.app_marketplace_app_compliance_report import generate_compliance_report, get_framework_controls

def test_compliant():
    controls = [{"id": "C1", "status": "pass"}, {"id": "C2", "status": "pass"}]
    r = generate_compliance_report(app_id="a1", framework="soc2", controls=controls)
    assert r["compliant"]
    assert r["compliance_pct"] == 100

def test_partial():
    controls = [{"id": "C1", "status": "pass"}, {"id": "C2", "status": "fail"}]
    r = generate_compliance_report(app_id="a1", framework="gdpr", controls=controls)
    assert not r["compliant"]
    assert r["compliance_pct"] == 50

def test_invalid_framework():
    r = generate_compliance_report(app_id="a1", framework="pci", controls=[])
    assert r["error"]

def test_get_controls():
    c = get_framework_controls(framework="soc2")
    assert len(c) == 4
    assert c[0]["id"] == "CC1.1"
