from app.services.app_marketplace_app_api_contract_testing import validate_response_against_contract, run_contract_suite

def test_valid():
    r = validate_response_against_contract(
        response={"status_code": 200, "body": {"id": "a1", "name": "App"}},
        contract={"status_code": 200, "required_fields": ["id", "name"], "field_types": {"name": "str"}})
    assert r["valid"]

def test_wrong_status():
    r = validate_response_against_contract(
        response={"status_code": 500, "body": {}}, contract={"status_code": 200})
    assert not r["valid"]

def test_missing_field():
    r = validate_response_against_contract(
        response={"status_code": 200, "body": {"id": "a1"}},
        contract={"status_code": 200, "required_fields": ["id", "name"]})
    assert not r["valid"]

def test_suite():
    contracts = [{"endpoint": "/users", "status_code": 200, "required_fields": ["id"]},
                 {"endpoint": "/apps", "status_code": 200, "required_fields": ["id"]}]
    responses = [{"status_code": 200, "body": {"id": "1"}},
                 {"status_code": 200, "body": {}}]
    r = run_contract_suite(contracts=contracts, responses=responses)
    assert r["passed"] == 1
    assert r["pass_rate"] == 50.0
