from app.services.app_marketplace_app_app_app_app_app_app_app_contract_tester import validate_response, run_contract_suite

def test_valid():
    r = validate_response(
        {"status": 200, "body": {"data": [], "meta": {}}, "headers": {"X-Request-Id": "abc"}},
        {"status": 200, "body_fields": ["data", "meta"], "headers": ["X-Request-Id"]})
    assert r["valid"]

def test_invalid():
    r = validate_response(
        {"status": 500, "body": {}, "headers": {}},
        {"status": 200, "body_fields": ["data"], "headers": ["X-Request-Id"]})
    assert not r["valid"]
    assert len(r["errors"]) == 3

def test_suite():
    tests = [
        {"name": "GET /users", "response": {"status": 200, "body": {"data": []}, "headers": {}},
         "contract": {"status": 200, "body_fields": ["data"]}},
        {"name": "GET /bad", "response": {"status": 500, "body": {}, "headers": {}},
         "contract": {"status": 200, "body_fields": ["data"]}},
    ]
    r = run_contract_suite(tests)
    assert r["total"] == 2
    assert r["passed"] == 1
    assert not r["all_passed"]
