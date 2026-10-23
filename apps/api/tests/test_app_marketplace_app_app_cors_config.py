from app.services.app_marketplace_app_app_cors_config import build_cors_policy

def test_basic():
    r = build_cors_policy(allowed_origins=["https://example.com"])
    assert r["valid"]
    assert "https://example.com" in r["allowed_origins"]
    assert "Access-Control-Allow-Origin" in r["headers"]

def test_wildcard_with_credentials():
    r = build_cors_policy(allowed_origins=["*"], credentials=True)
    assert not r["valid"]
    assert "wildcard" in r["errors"][0].lower()

def test_bad_scheme():
    r = build_cors_policy(allowed_origins=["ftp://bad.com"])
    assert not r["valid"]

def test_custom_methods():
    r = build_cors_policy(allowed_origins=["https://a.com"], allowed_methods=["GET", "POST"])
    assert r["allowed_methods"] == ["GET", "POST"]
