from app.services.app_marketplace_app_app_app_app_app_app_app_resp_header import inspect_headers

def test_valid():
    r = inspect_headers(
        {"Content-Type": "application/json", "X-Content-Type-Options": "nosniff",
         "X-Frame-Options": "DENY", "Strict-Transport-Security": "max-age=31536000",
         "Content-Security-Policy": "default-src 'self'"})
    assert r["valid"]
    assert r["secure"]

def test_missing_security():
    r = inspect_headers({"Content-Type": "application/json"})
    assert not r["secure"]
    assert len(r["issues"]) >= 2
