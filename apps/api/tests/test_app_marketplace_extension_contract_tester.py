from app.services.app_marketplace_extension_contract_tester import (
    ContractTesterService, RequestContract, ResponseContract
)


def _user_contract(svc):
    return svc.define_contract(
        consumer="frontend", provider="user-service",
        description="Get user by ID",
        request=RequestContract("GET", "/api/users/1"),
        response=ResponseContract(
            status=200,
            body_schema={"id": "integer", "name": "string", "email": "string", "active": "boolean"},
            required_fields=["id", "name"]))


def test_verify_pass():
    svc = ContractTesterService()
    contract = _user_contract(svc)
    result = svc.verify(contract.contract_id, 200,
                        {"id": 1, "name": "Alice", "email": "alice@test.com", "active": True})
    assert result.passed is True
    assert result.errors == []


def test_verify_wrong_status():
    svc = ContractTesterService()
    contract = _user_contract(svc)
    result = svc.verify(contract.contract_id, 404, {"error": "not found"})
    assert result.passed is False
    assert any("Status" in e for e in result.errors)


def test_verify_missing_required():
    svc = ContractTesterService()
    contract = _user_contract(svc)
    result = svc.verify(contract.contract_id, 200, {"id": 1})  # missing name
    assert result.passed is False
    assert any("name" in e for e in result.errors)


def test_verify_type_mismatch():
    svc = ContractTesterService()
    contract = _user_contract(svc)
    result = svc.verify(contract.contract_id, 200,
                        {"id": "not-an-int", "name": "Alice"})
    assert result.passed is False
    assert any("Type mismatch" in e and "id" in e for e in result.errors)


def test_verify_bool_not_int():
    svc = ContractTesterService()
    contract = _user_contract(svc)
    result = svc.verify(contract.contract_id, 200,
                        {"id": 1, "name": "Alice", "active": "yes"})
    assert result.passed is False
    assert any("active" in e for e in result.errors)


def test_optional_field_missing_ok():
    svc = ContractTesterService()
    contract = _user_contract(svc)
    # email is in schema but not required
    result = svc.verify(contract.contract_id, 200, {"id": 1, "name": "Alice"})
    assert result.passed is True


def test_verify_all():
    svc = ContractTesterService()
    _user_contract(svc)

    def handler(req):
        return 200, {"id": 1, "name": "Alice"}, {}

    results = svc.verify_all("user-service", handler)
    assert len(results) == 1
    assert results[0].passed is True


def test_backward_compat_ok():
    svc = ContractTesterService()
    contract = _user_contract(svc)
    # Adding optional field is backward compatible
    new_schema = {"id": "integer", "name": "string", "email": "string",
                  "active": "boolean", "avatar": "string"}
    issues = svc.check_backward_compat(contract.contract_id, new_schema, ["id", "name"])
    assert issues == []


def test_backward_compat_break():
    svc = ContractTesterService()
    contract = _user_contract(svc)
    # Removing 'name' field breaks consumers
    new_schema = {"id": "integer", "email": "string"}
    issues = svc.check_backward_compat(contract.contract_id, new_schema, ["id"])
    assert any("Removed field 'name'" in i for i in issues)


def test_backward_compat_type_change():
    svc = ContractTesterService()
    contract = _user_contract(svc)
    new_schema = {"id": "string", "name": "string", "email": "string", "active": "boolean"}
    issues = svc.check_backward_compat(contract.contract_id, new_schema, ["id", "name"])
    assert any("Type changed" in i and "id" in i for i in issues)
