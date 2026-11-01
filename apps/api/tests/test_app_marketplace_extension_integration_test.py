from app.services.app_marketplace_extension_integration_test import (
    ExtensionIntegrationTestService, TestOutcome,
)


def test_create_suite():
    svc = ExtensionIntegrationTestService()
    suite = svc.create_suite("ext-1")
    assert suite.suite_id.startswith("isuite_")


def test_add_tests_and_report():
    svc = ExtensionIntegrationTestService()
    suite = svc.create_suite("ext-1")
    svc.add_test(suite.suite_id, "test_install", "Install flow", TestOutcome.PASS, 500, 3)
    svc.add_test(suite.suite_id, "test_config", "Config flow", TestOutcome.PASS, 300, 2)
    svc.add_test(suite.suite_id, "test_webhook", "Webhook flow", TestOutcome.FAIL, 1000, 1, "Timeout")
    report = svc.get_report(suite.suite_id)
    assert report["total"] == 3
    assert report["passed"] == 2
    assert report["failed"] == 1
    assert report["pass_rate"] == 66.7


def test_get_failures():
    svc = ExtensionIntegrationTestService()
    suite = svc.create_suite("ext-1")
    svc.add_test(suite.suite_id, "ok", "s", TestOutcome.PASS)
    svc.add_test(suite.suite_id, "broken", "s", TestOutcome.FAIL, error="assertion failed")
    failures = svc.get_failures(suite.suite_id)
    assert len(failures) == 1
    assert failures[0].name == "broken"


def test_duration():
    svc = ExtensionIntegrationTestService()
    suite = svc.create_suite("ext-1")
    svc.add_test(suite.suite_id, "a", "s", TestOutcome.PASS, 100)
    svc.add_test(suite.suite_id, "b", "s", TestOutcome.PASS, 200)
    assert suite.total_duration_ms == 300
