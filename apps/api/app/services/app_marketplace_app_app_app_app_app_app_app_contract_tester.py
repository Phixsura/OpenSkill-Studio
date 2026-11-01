"""API contract tester — validate API responses against expected schemas."""
from __future__ import annotations


def validate_response(response: dict, contract: dict) -> dict:
    errors = []
    expected_status = contract.get("status")
    if expected_status and response.get("status") != expected_status:
        errors.append({"field": "status", "expected": expected_status,
                        "actual": response.get("status")})
    expected_fields = contract.get("body_fields", [])
    body = response.get("body", {})
    for field in expected_fields:
        if field not in body:
            errors.append({"field": f"body.{field}", "error": "missing"})
    expected_headers = contract.get("headers", [])
    headers = response.get("headers", {})
    for h in expected_headers:
        if h.lower() not in {k.lower() for k in headers}:
            errors.append({"field": f"header.{h}", "error": "missing"})
    return {"valid": len(errors) == 0, "errors": errors,
            "checks_passed": len(expected_fields) + 1 - len(errors),
            "total_checks": len(expected_fields) + len(expected_headers) + 1}


def run_contract_suite(tests: list[dict]) -> dict:
    results = []
    passed = 0
    for t in tests:
        r = validate_response(t["response"], t["contract"])
        r["name"] = t.get("name", "unnamed")
        results.append(r)
        if r["valid"]:
            passed += 1
    total = len(tests)
    return {"total": total, "passed": passed, "failed": total - passed,
            "pass_rate": round(passed / max(total, 1) * 100),
            "results": results, "all_passed": passed == total}
