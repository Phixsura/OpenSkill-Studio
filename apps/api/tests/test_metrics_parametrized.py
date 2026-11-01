"""Parametrized metrics tests."""

import pytest
from app.services.app_metrics import (
    METRIC_API_CALLS, METRIC_WEBHOOK_DELIVERIES, METRIC_WEBHOOK_FAILURES,
    METRIC_SANDBOX_EXECUTIONS, METRIC_SANDBOX_FAILURES, METRIC_EVENT_DISPATCHES,
    METRIC_INSTALLS, METRIC_UNINSTALLS,
    increment, get_count, record_api_call, record_webhook_delivery,
    record_sandbox_execution, record_event_dispatch, record_install, record_uninstall,
)

ALL_METRICS = [
    METRIC_API_CALLS, METRIC_WEBHOOK_DELIVERIES, METRIC_WEBHOOK_FAILURES,
    METRIC_SANDBOX_EXECUTIONS, METRIC_SANDBOX_FAILURES, METRIC_EVENT_DISPATCHES,
    METRIC_INSTALLS, METRIC_UNINSTALLS,
]

@pytest.mark.parametrize("metric", ALL_METRICS)
def test_metric_is_string(metric):
    assert isinstance(metric, str)
    assert len(metric) > 0

@pytest.mark.parametrize("metric", ALL_METRICS)
def test_metric_increment(metric):
    app_id = f"param-{metric}"
    increment(metric, app_id)
    assert get_count(metric, app_id) >= 1

RECORD_FNS = [
    ("api", record_api_call),
    ("webhook", lambda a: record_webhook_delivery(a, success=True)),
    ("sandbox", lambda a: record_sandbox_execution(a, success=True)),
    ("event", record_event_dispatch),
    ("install", record_install),
    ("uninstall", record_uninstall),
]

@pytest.mark.parametrize("name,fn", RECORD_FNS, ids=lambda x: x if isinstance(x, str) else "fn")
def test_record_function(name, fn):
    fn(f"param-record-{name}")
