"""Testing sandbox — isolated environment for app testing before publish."""

from datetime import datetime, timezone


def create_test_environment(*, app_id: str, version_id: str, developer_id: str,
                              config_overrides: dict | None = None) -> dict:
    return {
        "sandbox_id": f"sandbox_{app_id}_{version_id}",
        "app_id": app_id, "version_id": version_id, "developer_id": developer_id,
        "status": "provisioning", "config": config_overrides or {},
        "created_at": datetime.now(timezone.utc).isoformat(),
        "expires_at": None, "test_org_id": f"test_org_{app_id}",
        "endpoints": {"api": f"https://sandbox.openskill.dev/{app_id}/api",
                       "webhook": f"https://sandbox.openskill.dev/{app_id}/webhook"},
    }


def run_test_suite(*, sandbox_id: str, tests: list[dict]) -> dict:
    results = []
    passed = 0
    for t in tests:
        success = t.get("expected_status", 200) == t.get("actual_status", 200)
        results.append({"name": t["name"], "passed": success, "duration_ms": t.get("duration_ms", 0)})
        if success:
            passed += 1
    return {
        "sandbox_id": sandbox_id, "total": len(tests), "passed": passed,
        "failed": len(tests) - passed, "pass_rate": round(passed / max(len(tests), 1) * 100, 1),
        "results": results,
    }


def teardown_sandbox(*, sandbox_id: str) -> dict:
    return {"sandbox_id": sandbox_id, "status": "destroyed",
            "destroyed_at": datetime.now(timezone.utc).isoformat()}
