"""Tests for API Contract Validator service."""
import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_contract_validator import (
    ContractValidator, ContractSpec, FieldSpec,
)


class TestContractValidator:
    def test_valid_response(self):
        svc = ContractValidator()
        svc.register_contract(ContractSpec("c1", "ep1", "v1", [
            FieldSpec("name", "string"),
            FieldSpec("age", "int"),
        ]))
        result = svc.validate("c1", {"name": "Alice", "age": 30})
        assert result["valid"] is True

    def test_missing_required(self):
        svc = ContractValidator()
        svc.register_contract(ContractSpec("c1", "ep1", "v1", [
            FieldSpec("name", "string"),
            FieldSpec("email", "string"),
        ]))
        result = svc.validate("c1", {"name": "Alice"})
        assert result["valid"] is False
        assert result["errors"][0]["error"] == "missing_required_field"

    def test_type_mismatch(self):
        svc = ContractValidator()
        svc.register_contract(ContractSpec("c1", "ep1", "v1", [
            FieldSpec("count", "int"),
        ]))
        result = svc.validate("c1", {"count": "not_a_number"})
        assert result["valid"] is False
        assert result["errors"][0]["error"] == "type_mismatch"

    def test_bool_as_int_guard(self):
        svc = ContractValidator()
        svc.register_contract(ContractSpec("c1", "ep1", "v1", [
            FieldSpec("count", "int"),
        ]))
        result = svc.validate("c1", {"count": True})
        assert result["valid"] is False

    def test_nullable_field(self):
        svc = ContractValidator()
        svc.register_contract(ContractSpec("c1", "ep1", "v1", [
            FieldSpec("bio", "string", nullable=True),
        ]))
        result = svc.validate("c1", {"bio": None})
        assert result["valid"] is True

    def test_null_not_allowed(self):
        svc = ContractValidator()
        svc.register_contract(ContractSpec("c1", "ep1", "v1", [
            FieldSpec("name", "string", nullable=False),
        ]))
        result = svc.validate("c1", {"name": None})
        assert result["valid"] is False

    def test_extra_fields_reported(self):
        svc = ContractValidator()
        svc.register_contract(ContractSpec("c1", "ep1", "v1", [
            FieldSpec("id", "string"),
        ]))
        result = svc.validate("c1", {"id": "123", "secret": "x"})
        assert "secret" in result["extra_fields"]

    def test_diff_contracts(self):
        svc = ContractValidator()
        svc.register_contract(ContractSpec("c1", "ep1", "v1", [
            FieldSpec("name", "string"), FieldSpec("age", "int"),
        ]))
        svc.register_contract(ContractSpec("c2", "ep1", "v2", [
            FieldSpec("name", "string"), FieldSpec("email", "string"),
        ]))
        diff = svc.diff_contracts("c1", "c2")
        assert "email" in diff["added"]
        assert "age" in diff["removed"]
        assert diff["breaking"] is True

    def test_stats(self):
        svc = ContractValidator()
        svc.register_contract(ContractSpec("c1", "ep1", "v1", [FieldSpec("x", "string")]))
        svc.validate("c1", {"x": "ok"})
        svc.validate("c1", {"x": 123})
        stats = svc.get_stats()
        assert stats["passed"] == 1
        assert stats["failed"] == 1

    def test_empty_fields_rejected(self):
        svc = ContractValidator()
        with pytest.raises(ValueError):
            svc.register_contract(ContractSpec("c1", "ep1", "v1", []))

    def test_isolation(self):
        a, b = ContractValidator(), ContractValidator()
        a.register_contract(ContractSpec("c1", "ep1", "v1", [FieldSpec("x", "string")]))
        with pytest.raises(ValueError):
            b.validate("c1", {"x": "ok"})
