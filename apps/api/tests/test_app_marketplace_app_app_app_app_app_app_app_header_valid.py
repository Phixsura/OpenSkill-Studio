from app.services.app_marketplace_app_app_app_app_app_app_app_header_valid import validate_headers

def test_valid():
    r = validate_headers(
        {"Authorization": "Bearer xxx", "Content-Type": "application/json"},
        {"required": ["Authorization", "Content-Type"]})
    assert r["valid"]

def test_missing():
    r = validate_headers(
        {"Content-Type": "application/json"},
        {"required": ["Authorization"]})
    assert not r["valid"]
    assert r["errors"][0]["error"] == "missing_required"

def test_forbidden():
    r = validate_headers(
        {"X-Debug": "true", "Authorization": "xxx"},
        {"forbidden": ["X-Debug"]})
    assert not r["valid"]
    assert r["errors"][0]["error"] == "forbidden_header"
