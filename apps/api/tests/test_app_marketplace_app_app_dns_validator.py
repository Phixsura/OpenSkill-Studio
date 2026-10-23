from app.services.app_marketplace_app_app_dns_validator import validate_domain, generate_verification_record

def test_valid():
    r = validate_domain(domain="myapp.example.com")
    assert r["valid"]
    assert r["root"] == "example.com"
    assert r["subdomain"] == "myapp"

def test_root_domain():
    r = validate_domain(domain="example.com")
    assert r["valid"]
    assert r["subdomain"] is None

def test_invalid():
    r = validate_domain(domain="-bad..domain")
    assert not r["valid"]

def test_verification():
    r = generate_verification_record(domain="example.com", app_id="app123")
    assert r["type"] == "TXT"
    assert "openskill-verify=" in r["value"]
    assert len(r["token"]) == 32
