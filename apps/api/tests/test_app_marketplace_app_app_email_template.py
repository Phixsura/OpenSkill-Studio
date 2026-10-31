from app.services.app_marketplace_app_app_email_template import build_email, list_templates

def test_welcome():
    r = build_email(template_id="welcome", variables={"app_name": "SuperApp"})
    assert "SuperApp" in r["subject"]
    assert r["template_id"] == "welcome"

def test_billing():
    r = build_email(template_id="billing", variables={"app_name": "MyApp", "invoice_id": "INV-001"})
    assert "INV-001" in r["subject"]

def test_unknown():
    r = build_email(template_id="nonexistent", variables={})
    assert "error" in r

def test_list():
    t = list_templates()
    assert len(t) == 5
    assert any(x["id"] == "welcome" for x in t)
