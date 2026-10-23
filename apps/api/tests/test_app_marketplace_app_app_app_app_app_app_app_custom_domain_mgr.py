from app.services.app_marketplace_app_app_app_app_app_app_app_custom_domain_mgr import (
    add_domain, verify_domain, list_domains, remove_domain, clear_domains,
)

def test_lifecycle():
    clear_domains()
    r = add_domain("app1", "my-app.example.com")
    assert r["added"]
    assert "CNAME" in r["dns_record"]
    v = verify_domain("my-app.example.com")
    assert v["verified"]
    assert v["ssl"]
    domains = list_domains("app1")
    assert len(domains) == 1
    remove_domain("my-app.example.com")
    assert len(list_domains("app1")) == 0
    clear_domains()

def test_invalid():
    clear_domains()
    r = add_domain("app1", "not valid!")
    assert not r["added"]
    assert r["error"] == "invalid_domain"
    clear_domains()
