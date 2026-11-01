"""Integration test harness — structured test runner for app integrations."""

from datetime import datetime, timezone


def create_test_plan(*, app_id: str, scenarios: list[dict]) -> dict:
    return {
        "app_id": app_id, "scenarios": scenarios, "total": len(scenarios),
        "status": "pending", "created_at": datetime.now(timezone.utc).isoformat(),
    }


def execute_scenario(*, scenario: dict) -> dict:
    steps_results = []
    all_passed = True
    for step in scenario.get("steps", []):
        passed = step.get("mock_result", True)
        steps_results.append({"step": step["name"], "passed": passed, "output": step.get("output", "")})
        if not passed:
            all_passed = False
    return {
        "scenario": scenario["name"], "passed": all_passed,
        "steps": steps_results, "duration_ms": sum(s.get("duration_ms", 10) for s in scenario.get("steps", [])),
    }


def generate_test_report(*, plan: dict, results: list[dict]) -> dict:
    passed = sum(1 for r in results if r["passed"])
    return {
        "app_id": plan["app_id"], "total_scenarios": len(results),
        "passed": passed, "failed": len(results) - passed,
        "pass_rate": round(passed / max(len(results), 1) * 100, 1),
        "results": results, "generated_at": datetime.now(timezone.utc).isoformat(),
    }
