from app.services.app_marketplace_app_custom_domain import add_custom_domain, verify_domain, remove_custom_domain

def test_add():
    r = add_custom_domain(app_id="a1", domain="myapp.example.com")
    assert r["status"] == "pending_verification"
    assert "openskill.dev" in r["cname_target"]

def test_invalid():
    r = add_custom_domain(app_id="a1", domain="not valid!")
    assert r["error"]

def test_verify_ok():
    record = {"domain": "myapp.example.com", "cname_target": "a1.apps.openskill.dev"}
    r = verify_domain(domain_record=record, cname_value="a1.apps.openskill.dev")
    assert r["verified"]

def test_verify_fail():
    record = {"domain": "x.com", "cname_target": "a1.apps.openskill.dev"}
    r = verify_domain(domain_record=record, cname_value="wrong.target.com")
    assert not r["verified"]

def test_remove():
    r = remove_custom_domain(app_id="a1", domain="myapp.example.com")
    assert r["status"] == "removed"
