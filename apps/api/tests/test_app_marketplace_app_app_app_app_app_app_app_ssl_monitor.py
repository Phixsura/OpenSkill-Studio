from app.services.app_marketplace_app_app_app_app_app_app_app_ssl_monitor import check_certificates

def test_ssl():
    certs = [
        {"domain": "api.example.com", "issuer": "Let's Encrypt", "days_until_expiry": 60, "auto_renew": True},
        {"domain": "app.example.com", "issuer": "Let's Encrypt", "days_until_expiry": 15, "auto_renew": True},
        {"domain": "old.example.com", "issuer": "DigiCert", "days_until_expiry": -5, "auto_renew": False},
    ]
    r = check_certificates(certs)
    assert r["valid"] == 1
    assert r["expiring_soon"] == 1
    assert r["expired"] == 1
    assert r["overall"] == "critical"
    assert r["results"][0]["domain"] == "old.example.com"  # sorted by days_left
