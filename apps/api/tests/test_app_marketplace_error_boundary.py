from app.services.app_marketplace_error_boundary import build_error_response, is_retryable, get_all_error_codes

def test_error():
    r = build_error_response(code="APP_NOT_FOUND", details="App ID: a1")
    assert r["error"]["status"] == 404
    assert r["error"]["code"] == "APP_NOT_FOUND"
    assert r["error"]["details"] == "App ID: a1"

def test_unknown_code():
    r = build_error_response(code="UNKNOWN")
    assert r["error"]["status"] == 500

def test_retryable():
    assert is_retryable(code="RATE_LIMITED")
    assert is_retryable(code="SERVICE_UNAVAILABLE")
    assert not is_retryable(code="APP_NOT_FOUND")

def test_all_codes():
    codes = get_all_error_codes()
    assert len(codes) >= 9
    assert any(c["code"] == "UNAUTHORIZED" for c in codes)
