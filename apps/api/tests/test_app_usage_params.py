"""App usage service parameter tests."""

import inspect
import pytest
from app.services.app_usage import record_app_usage, get_app_usage_summary, get_installation_usage_summary

def test_record_has_action_or_type():
    params = set(inspect.signature(record_app_usage).parameters.keys())
    assert "action" in params or "event_type" in params or "usage_type" in params

def test_record_has_org_id():
    params = set(inspect.signature(record_app_usage).parameters.keys())
    assert "org_id" in params or "installation_id" in params or "app_id" in params

def test_summary_return_hint():
    hints = inspect.get_annotations(get_app_usage_summary)
    assert "return" in hints

def test_installation_summary_return_hint():
    hints = inspect.get_annotations(get_installation_usage_summary)
    assert "return" in hints

def test_all_async():
    for f in [record_app_usage, get_app_usage_summary, get_installation_usage_summary]:
        assert inspect.iscoroutinefunction(f)
