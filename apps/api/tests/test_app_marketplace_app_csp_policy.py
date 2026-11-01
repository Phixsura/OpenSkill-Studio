from app.services.app_marketplace_app_csp_policy import build_csp, validate_csp_origin

def test_basic():
    r = build_csp(app_id="a1", allowed_origins=[])
    assert "default-src 'self'" in r["header"]
    assert "frame-ancestors 'none'" in r["header"]

def test_with_origins():
    r = build_csp(app_id="a1", allowed_origins=["https://api.example.com"])
    assert "https://api.example.com" in r["header"]

def test_eval():
    r = build_csp(app_id="a1", allowed_origins=[], allow_eval=True)
    assert "'unsafe-eval'" in r["directives"]["script-src"]

def test_validate_ok():
    assert validate_csp_origin("https://example.com")
    assert validate_csp_origin("'self'")

def test_validate_bad():
    assert not validate_csp_origin("javascript:")
