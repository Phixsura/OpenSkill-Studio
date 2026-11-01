from app.services.app_marketplace_app_app_app_app_app_app_app_cert_mgr import create_cert, check_expiry, summarize_certs

def test_check():
    c = create_cert("example.com", validity_days=90)
    r = check_expiry(c)
    assert r["status"] == "valid"
    assert r["days_left"] > 80

def test_expired():
    c = create_cert("old.com", validity_days=1)
    r = check_expiry(c, now=c["issued_at"] + 86400 * 5)
    assert r["status"] == "expired"

def test_summary():
    certs = [create_cert("a.com", validity_days=90), create_cert("b.com", validity_days=90)]
    r = summarize_certs(certs)
    assert r["total"] == 2
    assert r["valid"] == 2
    assert not r["needs_action"]
