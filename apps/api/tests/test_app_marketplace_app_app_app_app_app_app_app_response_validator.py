from app.services.app_marketplace_app_app_app_app_app_app_app_response_validator import validate_api_response, check_status_code

def test_valid_single():
    r = validate_api_response({"data": {"id": "1", "name": "Test"}})
    assert r["valid"]
    assert r["response_type"] == "single"

def test_valid_list():
    r = validate_api_response({"data": [{"id": "1"}], "meta": {"total": 1, "page": 1}})
    assert r["valid"]
    assert r["response_type"] == "list"

def test_invalid():
    r = validate_api_response({"results": []})
    assert not r["valid"]
    r2 = validate_api_response({"data": [{"id": "1"}]})  # missing meta
    assert not r2["valid"]

def test_status():
    r = check_status_code(400, {"error": {"code": "BAD", "message": "bad"}})
    assert r["valid"]
    r2 = check_status_code(200, {"error": {"code": "X", "message": "y"}})
    assert not r2["valid"]
