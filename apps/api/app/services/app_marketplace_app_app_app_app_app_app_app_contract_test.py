"""API contract tester — validate API responses against contracts."""
from __future__ import annotations


def validate_contract(response: dict, contract: dict) -> dict:
    errors = []
    expected_status = contract.get("status")
    if expected_status and response.get("status") != expected_status:
        errors.append({"field": "status", "expected": expected_status, "actual": response.get("status")})
    body = response.get("body", {})
    for field, expected_type in contract.get("body_fields", {}).items():
        if field not in body:
            errors.append({"field": field, "error": "missing"})
        elif expected_type == "string" and not isinstance(body[field], str):
            errors.append({"field": field, "error": f"expected string, got {type(body[field]).__name__}"})
        elif expected_type == "number" and not isinstance(body[field], (int, float)):
            errors.append({"field": field, "error": f"expected number"})
    return {"valid": len(errors) == 0, "errors": errors, "contract": contract.get("name", "")}


def run_contract_suite(tests: list[dict]) -> dict:
    results = []
    for t in tests:
        r = validate_contract(t["response"], t["contract"])
        results.append({"name": t["contract"]["name"], "valid": r["valid"], "errors": len(r["errors"])})
    passed = sum(1 for r in results if r["valid"])
    return {"total": len(results), "passed": passed, "failed": len(results) - passed,
            "results": results}
