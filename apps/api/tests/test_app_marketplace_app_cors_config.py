from app.services.app_marketplace_app_cors_config import validate_cors_config

def test_valid():
    r = validate_cors_config(allowed_origins=["https://example.com", "http://localhost:3000"],
                              allowed_methods=["GET", "POST"])
    assert r["valid"]
    assert len(r["origins"]) == 2
    assert "GET" in r["methods"]

def test_wildcard():
    r = validate_cors_config(allowed_origins=["*"], allowed_methods=["GET"])
    assert r["valid"]
    assert not r["wildcard_warning"]

def test_invalid_origin():
    r = validate_cors_config(allowed_origins=["not-a-url"], allowed_methods=["GET"])
    assert not r["valid"]

def test_invalid_method():
    r = validate_cors_config(allowed_origins=["https://x.com"], allowed_methods=["EXPLODE"])
    assert not r["valid"]
