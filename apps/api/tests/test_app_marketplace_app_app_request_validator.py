from app.services.app_marketplace_app_app_request_validator import validate_request

def test_valid_get():
    r = validate_request(method="GET", path="/api/apps", headers={})
    assert r["valid"]

def test_missing_content_type():
    r = validate_request(method="POST", path="/api/apps", headers={}, body={"name": "App"})
    assert not r["valid"]
    assert any(e["field"] == "Content-Type" for e in r["errors"])

def test_missing_auth():
    r = validate_request(method="GET", path="/api/me", headers={},
        rules={"auth_required": True})
    assert not r["valid"]

def test_body_rules():
    rules = {"body_rules": {"name": {"required": True, "min_length": 3}}}
    r = validate_request(method="POST", path="/api/apps",
        headers={"Content-Type": "application/json"}, body={"name": "AB"}, rules=rules)
    assert not r["valid"]
    assert r["error_count"] == 1
