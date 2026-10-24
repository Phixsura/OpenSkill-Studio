from app.services.app_marketplace_app_csp_manager import build_csp, validate_csp

def test_build_default():
    r = build_csp()
    assert "default-src 'self'" in r["header_value"]
    assert r["directive_count"] == 7

def test_build_custom():
    r = build_csp(directives={"script-src": ["'self'", "https://cdn.example.com"]},
                   report_uri="https://report.example.com")
    assert "cdn.example.com" in r["header_value"]
    assert "report-uri" in r["header_value"]

def test_validate_secure():
    r = validate_csp(header="default-src 'self'; frame-ancestors 'none'")
    assert r["security_score"] == 100

def test_validate_warnings():
    r = validate_csp(header="script-src 'self' 'unsafe-inline' 'unsafe-eval'; img-src *")
    assert r["warning_count"] == 4  # unsafe-inline in script, unsafe-eval, wildcard
