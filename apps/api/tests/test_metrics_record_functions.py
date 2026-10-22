"""Parametrized metrics record function tests."""

import pytest
from app.services.app_metrics import (
    record_api_call, record_webhook_delivery, record_sandbox_execution,
    record_event_dispatch, record_install, record_uninstall, get_count,
    METRIC_API_CALLS, METRIC_WEBHOOK_DELIVERIES, METRIC_SANDBOX_EXECUTIONS,
    METRIC_EVENT_DISPATCHES, METRIC_INSTALLS, METRIC_UNINSTALLS,
)

RECORD_CASES = [
    (record_api_call, METRIC_API_CALLS),
    (record_event_dispatch, METRIC_EVENT_DISPATCHES),
    (record_install, METRIC_INSTALLS),
    (record_uninstall, METRIC_UNINSTALLS),
]

@pytest.mark.parametrize("fn,metric", RECORD_CASES)
def test_record_increments(fn, metric):
    app_id = f"mr-{metric}"
    fn(app_id)
    assert get_count(metric, app_id) >= 1

def test_webhook_success():
    record_webhook_delivery("mr-wh-s", success=True)
    assert get_count(METRIC_WEBHOOK_DELIVERIES, "mr-wh-s") >= 1

def test_webhook_failure():
    record_webhook_delivery("mr-wh-f", success=False)
    assert get_count("webhook_failures", "mr-wh-f") >= 1

def test_sandbox_success():
    record_sandbox_execution("mr-sb-s", success=True)
    assert get_count(METRIC_SANDBOX_EXECUTIONS, "mr-sb-s") >= 1

def test_sandbox_failure():
    record_sandbox_execution("mr-sb-f", success=False)
    assert get_count("sandbox_failures", "mr-sb-f") >= 1
