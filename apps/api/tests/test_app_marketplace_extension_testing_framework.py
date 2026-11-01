from app.services.app_marketplace_extension_testing_framework import (
    ExtensionTestRunner, TestCase, TestStatus, MockPlatformAPI,
)


def test_create_suite_and_add_results():
    runner = ExtensionTestRunner()
    suite = runner.create_suite("s1", "ext-1", "Unit Tests")
    assert suite.suite_id == "s1"
    runner.add_result("s1", TestCase("test_init", TestStatus.PASSED, 5.0, assertions=3))
    runner.add_result("s1", TestCase("test_process", TestStatus.PASSED, 12.0, assertions=5))
    runner.finish_suite("s1")
    summary = runner.get_summary("s1")
    assert summary["total"] == 2
    assert summary["all_passed"] is True
    assert summary["total_assertions"] == 8


def test_failed_suite():
    runner = ExtensionTestRunner()
    runner.create_suite("s2", "ext-2", "Integration")
    runner.add_result("s2", TestCase("test_ok", TestStatus.PASSED, 3.0))
    runner.add_result("s2", TestCase("test_bad", TestStatus.FAILED, 1.0, error_message="assert False"))
    summary = runner.get_summary("s2")
    assert summary["all_passed"] is False
    assert summary["by_status"]["failed"] == 1
    assert summary["pass_rate"] == 0.5


def test_mock_platform_api():
    api = MockPlatformAPI()
    api.set("config", {"theme": "dark"})
    assert api.get("config") == {"theme": "dark"}
    api.emit("action", {"type": "click"})
    assert len(api.get_events()) == 1
    api.reset()
    assert api.get("config") is None
    assert api.get_events() == []


def test_list_suites():
    runner = ExtensionTestRunner()
    runner.create_suite("s10", "ext-a", "Suite A")
    runner.create_suite("s11", "ext-a", "Suite B")
    runner.create_suite("s12", "ext-b", "Suite C")
    assert len(runner.list_suites("ext-a")) == 2


def test_skipped_and_error():
    runner = ExtensionTestRunner()
    runner.create_suite("s20", "ext-c", "Mixed")
    runner.add_result("s20", TestCase("skip", TestStatus.SKIPPED))
    runner.add_result("s20", TestCase("err", TestStatus.ERROR, error_message="RuntimeError"))
    runner.add_result("s20", TestCase("ok", TestStatus.PASSED, assertions=1))
    summary = runner.get_summary("s20")
    assert summary["by_status"]["skipped"] == 1
    assert summary["by_status"]["error"] == 1
    assert summary["all_passed"] is False
