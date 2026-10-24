from app.services.app_marketplace_app_app_app_app_app_app_app_contract_verify import verify_contract, verify_all_contracts

def test_compatible():
    r = verify_contract(
        {"name": "user-svc", "provides": {"id": "string", "name": "string", "email": "string"}},
        {"name": "order-svc", "requires": {"id": "string", "name": "string"}})
    assert r["compatible"]

def test_incompatible():
    r = verify_contract(
        {"name": "user-svc", "provides": {"id": "string"}},
        {"name": "order-svc", "requires": {"id": "string", "email": "string"}})
    assert not r["compatible"]
    assert "email" in r["missing_fields"]

def test_type_mismatch():
    r = verify_contract(
        {"name": "a", "provides": {"id": "string"}},
        {"name": "b", "requires": {"id": "number"}})
    assert not r["compatible"]
    assert r["type_mismatches"][0]["field"] == "id"
