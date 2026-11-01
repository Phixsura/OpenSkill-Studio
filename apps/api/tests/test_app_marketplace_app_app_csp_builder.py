from app.services.app_marketplace_app_app_csp_builder import build_csp, analyze_csp

def test_build_default():
    r = build_csp()
    assert "default-src 'self'" in r["header"]
    assert "frame-ancestors 'none'" in r["header"]
    assert r["directive_count"] == 9

def test_build_override():
    r = build_csp(overrides={"script-src": ["https://cdn.example.com"]})
    assert "https://cdn.example.com" in r["header"]

def test_analyze_good():
    r = analyze_csp(header="default-src 'self'; script-src 'self'; frame-ancestors 'none'")
    assert r["warning_count"] == 0

def test_analyze_warnings():
    r = analyze_csp(header="script-src 'self' 'unsafe-inline'")
    assert r["warning_count"] >= 2  # missing default-src + unsafe-inline
