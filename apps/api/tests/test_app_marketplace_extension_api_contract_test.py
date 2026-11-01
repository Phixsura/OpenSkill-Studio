from app.services.app_marketplace_extension_api_contract_test import (
    ApiContractTestService, ContractResult,
)


def test_define_contract():
    svc = ApiContractTestService()
    ct = svc.define_contract("ext-a", "ext-b", "/api/users", "GET",
                             response_fields=[{"field": "users", "type": "array"}])
    assert ct.method == "GET"
    assert len(ct.response_contract) == 1


def test_validate_pass():
    svc = ApiContractTestService()
    ct = svc.define_contract("a", "b", "/api/data", "GET",
                             response_fields=[
                                 {"field": "name", "type": "string"},
                                 {"field": "count", "type": "integer"},
                             ])
    result = svc.validate_response(ct.contract_id, {"name": "test", "count": 42})
    assert result.result == ContractResult.PASS


def test_validate_missing_field():
    svc = ApiContractTestService()
    ct = svc.define_contract("a", "b", "/api", "GET",
                             response_fields=[{"field": "id", "type": "string", "required": True}])
    result = svc.validate_response(ct.contract_id, {})
    assert result.result == ContractResult.FAIL
    assert any("Missing" in v for v in result.violations)


def test_validate_wrong_type():
    svc = ApiContractTestService()
    ct = svc.define_contract("a", "b", "/api", "GET",
                             response_fields=[{"field": "count", "type": "integer"}])
    result = svc.validate_response(ct.contract_id, {"count": "not_int"})
    assert result.result == ContractResult.FAIL


def test_validate_status_code():
    svc = ApiContractTestService()
    ct = svc.define_contract("a", "b", "/api", "POST", status_code=201)
    result = svc.validate_response(ct.contract_id, {}, actual_status=500)
    assert result.result == ContractResult.FAIL
    assert any("Status" in v for v in result.violations)


def test_extra_fields_warn():
    svc = ApiContractTestService()
    ct = svc.define_contract("a", "b", "/api", "GET",
                             response_fields=[{"field": "id", "type": "string"}])
    result = svc.validate_response(ct.contract_id, {"id": "1", "extra": "data"})
    assert result.result == ContractResult.WARN
    assert any("Unexpected" in w for w in result.warnings)


def test_nullable_field():
    svc = ApiContractTestService()
    ct = svc.define_contract("a", "b", "/api", "GET",
                             response_fields=[{"field": "bio", "type": "string", "nullable": True}])
    result = svc.validate_response(ct.contract_id, {})
    assert result.result == ContractResult.PASS  # nullable not required


def test_compatibility():
    svc = ApiContractTestService()
    ct = svc.define_contract("ext-a", "ext-b", "/api", "GET",
                             response_fields=[{"field": "ok", "type": "boolean"}])
    svc.validate_response(ct.contract_id, {"ok": True})
    compat = svc.get_compatibility("ext-a", "ext-b")
    assert compat["compatible"] is True
    assert compat["passed"] == 1
