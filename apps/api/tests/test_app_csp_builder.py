from app.services.app_csp_builder import build_extension_csp

def test_basic():
    csp = build_extension_csp(app_slug="my-app")
    assert "default-src 'none'" in csp
    assert "frame-ancestors" in csp

def test_with_hosts():
    csp = build_extension_csp(app_slug="x", allowed_hosts=["https://cdn.example.com"])
    assert "cdn.example.com" in csp

def test_no_unsafe_eval():
    csp = build_extension_csp(app_slug="x")
    assert "unsafe-eval" not in csp
