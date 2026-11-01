"""App stats aggregator tests."""
import pytest
from app.services.app_stats import compute_app_stats

def test_empty_stats():
    s = compute_app_stats()
    assert s["active_installs"] == 0
    assert s["execution_success_rate"] == 100.0

def test_with_installs():
    s = compute_app_stats(installs=100, uninstalls=20)
    assert s["active_installs"] == 80

def test_exec_success_rate():
    s = compute_app_stats(executions=100, errors=5)
    assert s["execution_success_rate"] == 95.0

def test_webhook_success_rate():
    s = compute_app_stats(webhooks_sent=200, webhooks_failed=10)
    assert s["webhook_success_rate"] == 95.0

def test_all_fields_present():
    s = compute_app_stats(installs=10, executions=50, webhooks_sent=20, api_calls=100)
    expected_keys = {"total_installs", "active_installs", "total_executions", "execution_success_rate",
                     "total_webhooks", "webhook_success_rate", "total_api_calls", "error_count"}
    assert expected_keys == set(s.keys())

def test_no_negative_installs():
    s = compute_app_stats(installs=5, uninstalls=10)
    assert s["active_installs"] == 0
