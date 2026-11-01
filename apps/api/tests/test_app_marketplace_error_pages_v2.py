from app.services.app_marketplace_error_pages_v2 import build_error_page_v2

def test_404():
    p = build_error_page_v2(status_code=404)
    assert p["title"] == "Page Not Found"
    assert p["action"]["url"] == "/marketplace"
    assert p["support_url"] is None

def test_500():
    p = build_error_page_v2(status_code=500, detail="DB connection failed")
    assert p["retryable"]
    assert p["detail"] == "DB connection failed"
    assert p["support_url"] == "/support"

def test_401():
    p = build_error_page_v2(status_code=401)
    assert p["action"]["label"] == "Sign In"
