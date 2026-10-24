"""App metrics — verify all recorder functions update counters."""

import pytest
from app.services.app_metrics import (
    record_api_call, record_webhook_delivery, record_sandbox_execution,
    record_event_dispatch, record_install, record_uninstall,
    get_all_counts,
)

def test_api_call_increments():
    app = "metrics-coverage-api"
    record_api_call(app)
    record_api_call(app)
    counts = get_all_counts(app)
    assert any(v >= 2 for v in counts.values())

def test_webhook_success_increments():
    app = "metrics-coverage-wh-ok"
    record_webhook_delivery(app, success=True)
    counts = get_all_counts(app)
    assert any(v >= 1 for v in counts.values())

def test_webhook_failure_increments():
    app = "metrics-coverage-wh-fail"
    record_webhook_delivery(app, success=False)
    counts = get_all_counts(app)
    assert any(v >= 1 for v in counts.values())

def test_sandbox_success():
    app = "metrics-coverage-sb-ok"
    record_sandbox_execution(app, success=True)
    counts = get_all_counts(app)
    assert any(v >= 1 for v in counts.values())

def test_sandbox_failure():
    app = "metrics-coverage-sb-fail"
    record_sandbox_execution(app, success=False)
    counts = get_all_counts(app)
    assert any(v >= 1 for v in counts.values())

def test_event_dispatch():
    app = "metrics-coverage-evt"
    record_event_dispatch(app)
    counts = get_all_counts(app)
    assert any(v >= 1 for v in counts.values())

def test_install_uninstall():
    app = "metrics-coverage-inst"
    record_install(app)
    record_uninstall(app)
    counts = get_all_counts(app)
    assert len(counts) >= 2
