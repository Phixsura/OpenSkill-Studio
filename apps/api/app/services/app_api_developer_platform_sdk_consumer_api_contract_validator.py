"""API Contract Validator — schema contract testing with diff detection."""
from __future__ import annotations

import structlog
from dataclasses import dataclass, field

logger = structlog.get_logger()


@dataclass
class FieldSpec:
    name: str
    field_type: str  # string, int, float, bool, object, array
    required: bool = True
    nullable: bool = False


@dataclass
class ContractSpec:
    contract_id: str
    endpoint_id: str
    version: str
    fields: list[FieldSpec] = field(default_factory=list)


@dataclass
class ContractValidator:
    """Validate API responses against contract specifications."""

    _contracts: dict[str, ContractSpec] = field(default_factory=dict)
    _validations: list[dict] = field(default_factory=list)

    def register_contract(self, contract: ContractSpec) -> dict:
        if contract.contract_id in self._contracts:
            raise ValueError(f"Contract {contract.contract_id} already exists")
        if not contract.fields:
            raise ValueError("Contract must have at least one field")
        self._contracts[contract.contract_id] = contract
        logger.info("contract_registered", contract_id=contract.contract_id)
        return {"contract_id": contract.contract_id, "field_count": len(contract.fields)}

    def validate(self, contract_id: str, response: dict) -> dict:
        contract = self._contracts.get(contract_id)
        if not contract:
            raise ValueError(f"Contract {contract_id} not found")
        errors: list[dict] = []
        type_map = {
            "string": str, "int": int, "float": (int, float),
            "bool": bool, "object": dict, "array": list,
        }
        for f in contract.fields:
            if f.name not in response:
                if f.required:
                    errors.append({"field": f.name, "error": "missing_required_field"})
                continue
            value = response[f.name]
            if value is None:
                if not f.nullable:
                    errors.append({"field": f.name, "error": "null_not_allowed"})
                continue
            expected_type = type_map.get(f.field_type)
            if expected_type:
                # bool-as-int guard
                if f.field_type == "int" and isinstance(value, bool):
                    errors.append({"field": f.name, "error": "type_mismatch",
                                   "expected": f.field_type, "got": "bool"})
                elif not isinstance(value, expected_type):
                    errors.append({"field": f.name, "error": "type_mismatch",
                                   "expected": f.field_type, "got": type(value).__name__})
        # Check extra fields
        known_fields = {f.name for f in contract.fields}
        extra = set(response.keys()) - known_fields
        valid = len(errors) == 0
        result = {
            "contract_id": contract_id,
            "valid": valid,
            "errors": errors,
            "extra_fields": sorted(extra),
            "checked_fields": len(contract.fields),
        }
        self._validations.append(result)
        return result

    def diff_contracts(self, id_a: str, id_b: str) -> dict:
        a = self._contracts.get(id_a)
        b = self._contracts.get(id_b)
        if not a or not b:
            raise ValueError("Both contracts must exist")
        fields_a = {f.name: f for f in a.fields}
        fields_b = {f.name: f for f in b.fields}
        added = sorted(set(fields_b) - set(fields_a))
        removed = sorted(set(fields_a) - set(fields_b))
        changed = []
        for name in sorted(set(fields_a) & set(fields_b)):
            fa, fb = fields_a[name], fields_b[name]
            if fa.field_type != fb.field_type or fa.required != fb.required or fa.nullable != fb.nullable:
                changed.append({"field": name, "from": fa.field_type, "to": fb.field_type})
        breaking = len(removed) > 0 or any(
            fields_b.get(c["field"], FieldSpec("", "")).required and not fields_a.get(c["field"], FieldSpec("", "")).required
            for c in changed
        )
        return {
            "from": id_a, "to": id_b,
            "added": added, "removed": removed, "changed": changed,
            "breaking": breaking or len(removed) > 0,
        }

    def get_stats(self) -> dict:
        total = len(self._validations)
        passed = sum(1 for v in self._validations if v["valid"])
        return {
            "total_contracts": len(self._contracts),
            "total_validations": total,
            "passed": passed,
            "failed": total - passed,
            "pass_rate": round(passed / total * 100, 1) if total > 0 else 0,
        }
