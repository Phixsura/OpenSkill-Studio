from app.services.app_marketplace_app_app_app_app_app_app_app_contract_reg import (
    register_contract, verify_contract, contract_summary,
)

def test_register_verify():
    c = register_contract("user-svc", "api-gw", "1.0", {"fields": ["id", "name", "email"]})
    assert c["field_count"] == 3
    r = verify_contract(c, {"id": 1, "name": "Alice", "email": "a@b.com"})
    assert r["valid"]
    assert r["compliance_pct"] == 100
    r2 = verify_contract(c, {"id": 1, "name": "Alice"})
    assert not r2["valid"]
    assert "email" in r2["missing_fields"]

def test_summary():
    contracts = [
        register_contract("a", "b", "1.0", {"fields": []}),
        register_contract("a", "c", "1.0", {"fields": []}),
        register_contract("d", "b", "1.0", {"fields": []}),
    ]
    r = contract_summary(contracts)
    assert r["total"] == 3
    assert r["by_provider"]["a"] == 2
