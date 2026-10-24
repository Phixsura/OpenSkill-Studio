from app.services.app_marketplace_app_app_app_app_app_app_app_contract_test import validate_contract, run_contract_suite

def test_valid():
    r = validate_contract(
        {"status": 200, "body": {"id": "u1", "name": "Alice", "age": 30}},
        {"name": "get_user", "status": 200, "body_fields": {"id": "string", "name": "string", "age": "number"}})
    assert r["valid"]

def test_invalid():
    r = validate_contract(
        {"status": 200, "body": {"id": 123}},
        {"name": "get_user", "status": 200, "body_fields": {"id": "string", "name": "string"}})
    assert not r["valid"]
    assert len(r["errors"]) == 2  # id wrong type + name missing

def test_suite():
    r = run_contract_suite([
        {"response": {"status": 200, "body": {"ok": True}}, "contract": {"name": "t1", "status": 200, "body_fields": {}}},
        {"response": {"status": 500, "body": {}}, "contract": {"name": "t2", "status": 200, "body_fields": {}}},
    ])
    assert r["passed"] == 1
    assert r["failed"] == 1
