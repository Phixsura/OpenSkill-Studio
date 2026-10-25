"""API Contract — define and enforce API contracts between extensions.

Manages typed API contracts that extensions expose, enabling
type-safe inter-extension communication and backward compatibility.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum


class ContractStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    DEPRECATED = "deprecated"


@dataclass
class ContractMethod:
    name: str
    input_schema: dict
    output_schema: dict
    description: str = ""


@dataclass
class APIContract:
    contract_id: str
    extension_id: str
    version: int
    methods: list[ContractMethod]
    status: ContractStatus = ContractStatus.DRAFT
    description: str = ""


class APIContractService:
    """Manages API contracts between extensions."""

    def __init__(self):
        self._contracts: dict[str, APIContract] = {}

    def register(self, contract: APIContract) -> APIContract:
        key = f"{contract.extension_id}:v{contract.version}"
        self._contracts[key] = contract
        return contract

    def publish(self, extension_id: str, version: int) -> bool:
        key = f"{extension_id}:v{version}"
        c = self._contracts.get(key)
        if c and c.status == ContractStatus.DRAFT:
            c.status = ContractStatus.PUBLISHED
            return True
        return False

    def deprecate(self, extension_id: str, version: int) -> bool:
        key = f"{extension_id}:v{version}"
        c = self._contracts.get(key)
        if c and c.status == ContractStatus.PUBLISHED:
            c.status = ContractStatus.DEPRECATED
            return True
        return False

    def get_contract(self, extension_id: str, version: int) -> APIContract | None:
        return self._contracts.get(f"{extension_id}:v{version}")

    def get_latest(self, extension_id: str) -> APIContract | None:
        versions = [c for c in self._contracts.values()
                    if c.extension_id == extension_id and c.status != ContractStatus.DEPRECATED]
        if not versions:
            return None
        return max(versions, key=lambda c: c.version)

    def validate_call(self, extension_id: str, method_name: str,
                      input_data: dict, version: int | None = None) -> tuple[bool, list[str]]:
        """Validate a method call against the contract."""
        contract = (self.get_contract(extension_id, version) if version
                    else self.get_latest(extension_id))
        if not contract:
            return False, ["No contract found"]

        method = next((m for m in contract.methods if m.name == method_name), None)
        if not method:
            return False, [f"Method '{method_name}' not found in contract"]

        # Basic schema validation
        errors = []
        required = method.input_schema.get("required", [])
        for field_name in required:
            if field_name not in input_data:
                errors.append(f"Missing required field: {field_name}")

        properties = method.input_schema.get("properties", {})
        type_map = {"string": str, "integer": int, "boolean": bool, "array": list, "object": dict}
        for field_name, field_def in properties.items():
            if field_name in input_data:
                expected = type_map.get(field_def.get("type", ""))
                if expected and not isinstance(input_data[field_name], expected):
                    errors.append(f"Field '{field_name}': expected {field_def['type']}")

        return len(errors) == 0, errors

    def check_compatibility(self, extension_id: str, old_ver: int, new_ver: int) -> dict:
        """Check backward compatibility between contract versions."""
        old = self.get_contract(extension_id, old_ver)
        new = self.get_contract(extension_id, new_ver)
        if not old or not new:
            return {"compatible": False, "reason": "Version not found"}

        old_methods = {m.name for m in old.methods}
        new_methods = {m.name for m in new.methods}
        removed = old_methods - new_methods
        added = new_methods - old_methods

        return {
            "compatible": len(removed) == 0,
            "methods_added": sorted(added),
            "methods_removed": sorted(removed),
            "breaking": len(removed) > 0,
        }
