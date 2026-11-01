from app.services.app_marketplace_app_app_app_custom_domain_config import configure_custom_domain, check_domain_status

def test_configure():
    r = configure_custom_domain(domain="myapp.example.com", app_id="app_123")
    assert r["domain"] == "myapp.example.com"
    assert r["status"] == "pending_verification"
    assert len(r["dns_records"]) == 2
    assert r["ssl"]["auto_renew"]

def test_invalid():
    r = configure_custom_domain(domain="-bad..", app_id="x")
    assert "error" in r

def test_active():
    r = check_domain_status(verified=True, ssl_active=True)
    assert r["status"] == "active"
    assert r["icon"] == "🟢"

def test_pending():
    r = check_domain_status(verified=False, ssl_active=False)
    assert r["status"] == "pending"
