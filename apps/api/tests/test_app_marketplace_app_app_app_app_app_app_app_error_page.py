from app.services.app_marketplace_app_app_app_app_app_app_app_error_page import generate_error, error_summary

def test_generate():
    r = generate_error(404, "User not found", "req-123")
    assert r["error"]["code"] == "NOT_FOUND"
    assert r["error"]["status"] == 404
    assert r["error"]["request_id"] == "req-123"

def test_unknown():
    r = generate_error(418, "I'm a teapot")
    assert r["error"]["code"] == "UNKNOWN"

def test_summary():
    errors = [generate_error(404), generate_error(404), generate_error(500)]
    r = error_summary(errors)
    assert r["total"] == 3
    assert r["most_common"] == "NOT_FOUND"
