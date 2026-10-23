from app.services.app_marketplace_custom_domain import validate_domain, setup_custom_domain, check_domain_status

def test_valid():
    r = validate_domain(domain="myapp.example.com")
    assert r["valid"]

def test_invalid():
    r = validate_domain(domain="not a domain!")
    assert not r["valid"]

def test_reserved():
    r = validate_domain(domain="evil.openskill.dev")
    assert not r["valid"]

def test_setup():
    r = setup_custom_domain(app_id="a1", domain="myapp.example.com")
    assert r["success"]
    assert len(r["dns_records"]) == 2
    assert r["ssl_status"] == "pending"

def test_status():
    r = check_domain_status(domain="myapp.example.com")
    assert r["ssl_status"] == "active"
