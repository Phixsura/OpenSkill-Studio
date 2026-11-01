"""App testing framework — structured testing utilities for app developers."""


def create_test_fixture(*, name: str, setup_data: dict, teardown_actions: list[str] | None = None) -> dict:
    return {"name": name, "setup_data": setup_data, "teardown_actions": teardown_actions or [],
            "reusable": True, "status": "ready"}


def run_assertion(*, actual: object, expected: object, operator: str = "eq") -> dict:
    ops = {"eq": actual == expected, "ne": actual != expected,
           "gt": actual > expected if isinstance(actual, (int, float)) and isinstance(expected, (int, float)) else False,
           "contains": expected in actual if isinstance(actual, (str, list, dict)) else False}
    passed = ops.get(operator, False)
    return {"passed": passed, "actual": actual, "expected": expected, "operator": operator,
            "message": "OK" if passed else f"Expected {actual} {operator} {expected}"}


def build_test_report(*, suite_name: str, results: list[dict]) -> dict:
    passed = sum(1 for r in results if r.get("passed"))
    failed = len(results) - passed
    return {"suite": suite_name, "total": len(results), "passed": passed, "failed": failed,
            "pass_rate": round(passed / max(len(results), 1) * 100, 1),
            "status": "green" if failed == 0 else "red"}
