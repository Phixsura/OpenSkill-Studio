"""API contract testing — verify API contracts between services."""
from __future__ import annotations


def verify_contract(contract: dict, actual_response: dict) -> dict:
    errors = []
    required_fields = contract.get("required_fields", [])
    for field in required_fields:
        if field not in actual_response:
            errors.append({"field": field, "error": "missing_required_field"})
    type_checks = contract.get("field_types", {})
    type_map = {"string": str, "number": (int, float), "boolean": bool, "array": list, "object": dict}
    for field, expected_type in type_checks.items():
        if field in actual_response:
            py_type = type_map.get(expected_type)
            if py_type and not isinstance(actual_response[field], py_type):
                errors.append({"field": field, "error": f"expected_{expected_type}",
                               "got": type(actual_response[field]).__name__})
    status = contract.get("expected_status")
    actual_status = actual_response.get("_status")
    if status and actual_status and status != actual_status:
        errors.append({"field": "_status", "error": f"expected_{status}_got_{actual_status}"})
    return {"valid": len(errors) == 0, "errors": errors, "error_count": len(errors),
            "contract_name": contract.get("name", ""), "fields_checked": len(required_fields) + len(type_checks)}


def contract_summary(results: list[dict]) -> dict:
    passed = sum(1 for r in results if r["valid"])
    return {"total": len(results), "passed": passed, "failed": len(results) - passed,
            "pass_rate": round(passed / max(len(results), 1) * 100)}
