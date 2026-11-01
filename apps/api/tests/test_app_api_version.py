from app.services.app_api_version import is_supported, get_version_header, validate_request_version, CURRENT_VERSION

def test_current_supported():
    assert is_supported(CURRENT_VERSION) is True

def test_unknown_not_supported():
    assert is_supported("1999-01-01") is False

def test_version_header():
    h = get_version_header()
    assert h["X-API-Version"] == CURRENT_VERSION

def test_validate_none():
    r = validate_request_version(None)
    assert r["valid"] is True
    assert r["using_default"] is True

def test_validate_current():
    r = validate_request_version(CURRENT_VERSION)
    assert r["valid"] is True

def test_validate_unknown():
    r = validate_request_version("2099-01-01")
    assert r["valid"] is False
