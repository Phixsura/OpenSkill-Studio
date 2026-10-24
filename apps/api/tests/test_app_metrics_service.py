"""App metrics service tests."""

import pytest
from app.services.app_metrics import (
    increment, get_count, get_all_counts,
    record_api_call, record_webhook_delivery, record_sandbox_execution,
    record_event_dispatch, record_install, record_uninstall,
)

RECORDERS = [
    record_api_call, record_webhook_delivery, record_sandbox_execution,
    record_event_dispatch, record_install, record_uninstall,
]

@pytest.mark.parametrize("recorder", RECORDERS, ids=lambda f: f.__name__)
def test_recorder_runs(recorder):
    if recorder in (record_webhook_delivery, record_sandbox_execution):
        recorder("metrics-test-app", success=True)
    else:
        recorder("metrics-test-app")

def test_increment_and_get():
    increment("test_metric", "app-inc-001", amount=5)
    count = get_count("test_metric", "app-inc-001")
    assert count >= 5

def test_increment_default_amount():
    increment("default_metric", "app-inc-002")
    assert get_count("default_metric", "app-inc-002") >= 1

def test_get_all_counts():
    increment("m1", "app-all-001")
    increment("m2", "app-all-001")
    result = get_all_counts("app-all-001")
    assert isinstance(result, dict)
    assert "m1" in result
    assert "m2" in result

def test_get_count_zero_for_unknown():
    count = get_count("nonexistent_metric", "no-such-app-xyz")
    assert count == 0

def test_webhook_failure():
    record_webhook_delivery("app-fail-001", success=False)

def test_sandbox_failure():
    record_sandbox_execution("app-fail-002", success=False)
