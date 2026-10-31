from app.services.app_marketplace_developer_verification import initiate_domain_verification, check_verification, get_verification_badge

def test_initiate():
    r = initiate_domain_verification(developer_id="d1", domain="example.com")
    assert r["status"] == "pending"
    assert r["txt_record"].startswith("openskill-verify=")

def test_invalid_domain():
    r = initiate_domain_verification(developer_id="d1", domain="not a domain")
    assert r["error"]

def test_check_ok():
    r = initiate_domain_verification(developer_id="d1", domain="example.com")
    c = check_verification(expected_token=r["verification_token"], found_records=[r["txt_record"]])
    assert c["verified"]

def test_check_fail():
    c = check_verification(expected_token="abc", found_records=["openskill-verify=xyz"])
    assert not c["verified"]

def test_badge_trusted():
    b = get_verification_badge(verified_domain=True, verified_email=True, published_apps=5)
    assert b["level"] == "trusted"

def test_badge_basic():
    b = get_verification_badge(verified_domain=False, verified_email=True, published_apps=0)
    assert b["level"] == "basic"
