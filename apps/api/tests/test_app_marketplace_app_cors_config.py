from app.services.app_marketplace_app_cors_config import validate_origin, build_cors_config

def test_valid_origin():
    r = validate_origin("https://example.com")
    assert r["valid"]

def test_wildcard_warning():
    r = validate_origin("*")
    assert r["valid"]
    assert r["warning"]

def test_invalid():
    r = validate_origin("not-a-url")
    assert not r["valid"]

def test_config():
    c = build_cors_config(allowed_origins=["https://app.com", "https://dev.app.com"])
    assert c["valid"]
    assert c["allow_credentials"]

def test_config_wildcard():
    c = build_cors_config(allowed_origins=["*"])
    assert not c["allow_credentials"]
