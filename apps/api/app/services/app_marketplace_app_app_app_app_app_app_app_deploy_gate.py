"""Deployment gate checker — verify all gates pass before deployment."""
from __future__ import annotations


def check_gates(gates: list[dict]) -> dict:
    results = []
    for gate in gates:
        passed = gate.get("passed", False)
        results.append({"name": gate["name"], "passed": passed,
                        "required": gate.get("required", True),
                        "details": gate.get("details", "")})
    all_required_passed = all(r["passed"] for r in results if r["required"])
    failed_required = [r["name"] for r in results if r["required"] and not r["passed"]]
    return {"can_deploy": all_required_passed, "gates": results,
            "total": len(results),
            "passed": sum(1 for r in results if r["passed"]),
            "failed_required": failed_required}


def standard_gates() -> list[dict]:
    return [
        {"name": "unit_tests", "required": True},
        {"name": "integration_tests", "required": True},
        {"name": "security_scan", "required": True},
        {"name": "code_review", "required": True},
        {"name": "load_test", "required": False},
        {"name": "manual_approval", "required": False},
    ]
