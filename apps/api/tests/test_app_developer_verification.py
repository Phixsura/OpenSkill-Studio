from app.services.app_developer_verification import create_verification_code, verify_code, generate_domain_challenge

def test_create_and_verify():
    code = create_verification_code(developer_id="d1", email="dev@x.com")
    result = verify_code(code)
    assert result is not None
    assert result["verified"] is True
    assert result["developer_id"] == "d1"

def test_one_time_use():
    code = create_verification_code(developer_id="d2", email="a@b.c")
    verify_code(code)
    assert verify_code(code) is None

def test_unknown_code():
    assert verify_code("nonexistent") is None

def test_domain_challenge():
    ch = generate_domain_challenge("example.com")
    assert ch["type"] == "dns_txt"
    assert ch["domain"] == "example.com"
    assert ch["record_name"] == "_openskill-verify"
    assert len(ch["record_value"]) == 32

def test_unique_challenges():
    c1 = generate_domain_challenge("a.com")
    c2 = generate_domain_challenge("a.com")
    assert c1["record_value"] != c2["record_value"]
