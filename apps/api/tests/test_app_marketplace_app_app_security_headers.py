from app.services.app_marketplace_app_app_security_headers import generate_security_headers, audit_security_headers

def test_generate():
    r = generate_security_headers()
    assert r["total"] == 6
    assert "nosniff" in r["headers"]["X-Content-Type-Options"]

def test_custom():
    r = generate_security_headers(custom={"X-Custom": "value"})
    assert "X-Custom" in r["headers"]
    assert r["total"] == 7

def test_audit_perfect():
    r = audit_security_headers(current_headers={
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
        "X-Content-Type-Options": "nosniff", "X-Frame-Options": "DENY",
        "X-XSS-Protection": "0", "Referrer-Policy": "strict-origin-when-cross-origin",
        "Permissions-Policy": "camera=(), microphone=(), geolocation=()"})
    assert r["grade"] == "A"
    assert r["score"] == 100

def test_audit_missing():
    r = audit_security_headers(current_headers={"X-Content-Type-Options": "nosniff"})
    assert r["grade"] in ("C", "F")
    assert len(r["findings"]) >= 4
