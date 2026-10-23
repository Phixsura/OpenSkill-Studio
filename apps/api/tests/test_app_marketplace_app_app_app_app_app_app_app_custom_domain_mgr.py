from app.services.app_marketplace_app_app_app_app_app_app_app_custom_domain_mgr import (
    validate_domain, configure_domain, verify_domain)

def test_validate():
    assert validate_domain("app.example.com")["valid"]
    assert validate_domain("example.com")["valid"]
    assert not validate_domain("not valid!")["valid"]

def test_configure():
    r = configure_domain("app.example.com")
    assert r["status"] == "pending_verification"
    assert len(r["dns_records"]) == 2
    assert r["dns_records"][0]["type"] == "CNAME"

def test_verify():
    r = verify_domain("app.example.com", txt_records=["openskill-verify-app-example-com"])
    assert r["verified"]
    assert r["status"] == "active"
    r2 = verify_domain("app.example.com", txt_records=[])
    assert not r2["verified"]
