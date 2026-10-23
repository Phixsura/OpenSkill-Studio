from app.services.app_marketplace_app_app_app_app_app_app_app_contract_test import verify_contract, contract_summary

def test_valid():
    contract = {"name": "get_user", "required_fields": ["id", "name"],
                "field_types": {"id": "string", "name": "string", "age": "number"}}
    r = verify_contract(contract, {"id": "u1", "name": "Alice", "age": 30})
    assert r["valid"]
    assert r["error_count"] == 0

def test_invalid():
    contract = {"name": "get_user", "required_fields": ["id", "email"],
                "field_types": {"id": "number"}}
    r = verify_contract(contract, {"id": "not_a_number"})
    assert not r["valid"]
    assert r["error_count"] == 2  # missing email + wrong type

def test_summary():
    results = [{"valid": True}, {"valid": True}, {"valid": False}]
    s = contract_summary(results)
    assert s["passed"] == 2
    assert s["pass_rate"] == 67
