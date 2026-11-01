from app.services.app_marketplace_extension_sandbox_test_runner import (
    SandboxTestRunnerService, TestResult,
)


def test_run_suite():
    svc = SandboxTestRunnerService()
    result = svc.run_suite("sb-1", "unit_tests", [
        {"name": "test_add", "result": "passed", "duration_ms": 5, "assertions": 3},
        {"name": "test_sub", "result": "passed", "duration_ms": 3, "assertions": 2},
        {"name": "test_div", "result": "failed", "duration_ms": 8, "error": "Division by zero"},
    ])
    assert result.passed == 2
    assert result.failed == 1
    assert result.total == 3
    assert result.pass_rate == 66.7


def test_all_passed():
    svc = SandboxTestRunnerService()
    result = svc.run_suite("sb-1", "smoke", [
        {"name": "test_health", "assertions": 1},
        {"name": "test_login", "assertions": 2},
    ])
    assert result.pass_rate == 100.0


def test_summary():
    svc = SandboxTestRunnerService()
    svc.run_suite("sb-1", "suite1", [
        {"name": "a", "assertions": 2},
        {"name": "b", "result": "failed"},
    ])
    svc.run_suite("sb-1", "suite2", [
        {"name": "c", "assertions": 3},
    ])
    summary = svc.get_summary("sb-1")
    assert summary["suites_run"] == 2
    assert summary["total_tests"] == 3
    assert summary["passed"] == 2
    assert summary["failed"] == 1
    assert summary["total_assertions"] == 6


def test_failed_tests():
    svc = SandboxTestRunnerService()
    svc.run_suite("sb-1", "tests", [
        {"name": "ok", "result": "passed"},
        {"name": "broken", "result": "failed", "error": "assertion error"},
        {"name": "crash", "result": "error", "error": "segfault"},
    ])
    failed = svc.get_failed_tests("sb-1")
    assert len(failed) == 2
    assert failed[0].name == "broken"


def test_skipped():
    svc = SandboxTestRunnerService()
    result = svc.run_suite("sb-1", "tests", [
        {"name": "skip_me", "result": "skipped"},
        {"name": "run_me"},
    ])
    assert result.skipped == 1
    assert result.passed == 1


def test_latest():
    svc = SandboxTestRunnerService()
    svc.run_suite("sb-1", "first", [{"name": "a"}])
    svc.run_suite("sb-1", "second", [{"name": "b"}])
    latest = svc.get_latest("sb-1")
    assert latest.suite_name == "second"


def test_clear():
    svc = SandboxTestRunnerService()
    svc.run_suite("sb-1", "tests", [{"name": "a"}])
    assert svc.clear("sb-1") == 1
    assert svc.get_latest("sb-1") is None
