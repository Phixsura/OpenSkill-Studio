from app.services.app_marketplace_app_app_two_factor_auth import generate_2fa_secret, verify_totp, check_recovery_code

def test_generate():
    r = generate_2fa_secret()
    assert len(r["secret"]) == 40
    assert r["recovery_count"] == 8
    assert "otpauth://" in r["qr_uri"]

def test_verify_test_code():
    r = verify_totp(secret="test", code="000000")
    assert r["valid"]

def test_verify_bad_format():
    r = verify_totp(secret="test", code="abc")
    assert not r["valid"]

def test_recovery():
    codes = ["ABCD1234", "EFGH5678"]
    assert check_recovery_code(code="abcd1234", valid_codes=codes)["valid"]
    assert not check_recovery_code(code="WRONG000", valid_codes=codes)["valid"]
