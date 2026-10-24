from app.services.app_marketplace_app_certificate_manager import issue_certificate, check_certificate_health

def test_issue_auto():
    r = issue_certificate(domain="myapp.example.com")
    assert r["cert_id"].startswith("cert_")
    assert r["auto_renew"]
    assert r["issuer"] == "Let's Encrypt"

def test_issue_custom():
    r = issue_certificate(domain="x.com", cert_type="custom")
    assert not r["auto_renew"]

def test_invalid_type():
    r = issue_certificate(domain="x.com", cert_type="magic")
    assert "error" in r

def test_health():
    certs = [
        {"domain": "a.com", "expires_at": "2027-01-01T00:00:00", "auto_renew": True},
        {"domain": "b.com", "expires_at": "2026-10-25T00:00:00", "auto_renew": False},
    ]
    r = check_certificate_health(certificates=certs)
    assert r["total"] == 2
    assert r["certificates"][0]["status"] == "valid"
