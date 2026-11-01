"""Tests for app metrics service."""

from app.services.app_metrics import (
    METRIC_API_CALLS,
    METRIC_SANDBOX_EXECUTIONS,
    METRIC_WEBHOOK_DELIVERIES,
    get_all_counts,
    get_count,
    increment,
    record_api_call,
    record_install,
    record_sandbox_execution,
    record_uninstall,
    record_webhook_delivery,
)


def test_increment_and_get():
    increment("test_metric", "app-m1")
    increment("test_metric", "app-m1")
    assert get_count("test_metric", "app-m1") >= 2


def test_get_zero_for_unknown():
    assert get_count("nonexistent_metric", "nonexistent_app") == 0


def test_record_api_call():
    record_api_call("app-m2")
    assert get_count(METRIC_API_CALLS, "app-m2") >= 1


def test_record_webhook_success():
    record_webhook_delivery("app-m3", success=True)
    assert get_count(METRIC_WEBHOOK_DELIVERIES, "app-m3") >= 1


def test_record_webhook_failure():
    record_webhook_delivery("app-m4", success=False)
    assert get_count(METRIC_WEBHOOK_DELIVERIES, "app-m4") >= 1
    assert get_count("webhook_failures", "app-m4") >= 1


def test_record_sandbox_success():
    record_sandbox_execution("app-m5", success=True)
    assert get_count(METRIC_SANDBOX_EXECUTIONS, "app-m5") >= 1


def test_record_sandbox_failure():
    record_sandbox_execution("app-m6", success=False)
    assert get_count("sandbox_failures", "app-m6") >= 1


def test_record_install_uninstall():
    record_install("app-m7")
    record_uninstall("app-m7")
    assert get_count("installs", "app-m7") >= 1
    assert get_count("uninstalls", "app-m7") >= 1


def test_get_all_counts():
    record_api_call("app-m8")
    record_webhook_delivery("app-m8")
    record_sandbox_execution("app-m8")
    counts = get_all_counts("app-m8")
    assert counts.get(METRIC_API_CALLS, 0) >= 1
    assert counts.get(METRIC_WEBHOOK_DELIVERIES, 0) >= 1
    assert counts.get(METRIC_SANDBOX_EXECUTIONS, 0) >= 1


def test_isolation_between_apps():
    increment("isolated_metric", "app-iso-1", 5)
    increment("isolated_metric", "app-iso-2", 3)
    assert get_count("isolated_metric", "app-iso-1") >= 5
    assert get_count("isolated_metric", "app-iso-2") >= 3
