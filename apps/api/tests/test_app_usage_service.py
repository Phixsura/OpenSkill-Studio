"""App usage metering service tests."""

import inspect
import pytest
from app.services.app_usage import record_app_usage, get_app_usage_summary, get_installation_usage_summary


FUNCS = [record_app_usage, get_app_usage_summary, get_installation_usage_summary]

@pytest.mark.parametrize("func", FUNCS, ids=lambda f: f.__name__)
def test_all_async(func):
    assert inspect.iscoroutinefunction(func)

@pytest.mark.parametrize("func", FUNCS, ids=lambda f: f.__name__)
def test_requires_db(func):
    assert "db" in inspect.signature(func).parameters

def test_record_requires_app_id():
    assert "app_id" in inspect.signature(record_app_usage).parameters

def test_record_requires_action():
    params = inspect.signature(record_app_usage).parameters
    assert "action" in params or "event_type" in params or "usage_type" in params

def test_get_app_summary_requires_app_id():
    assert "app_id" in inspect.signature(get_app_usage_summary).parameters

def test_get_installation_summary_requires_installation_id():
    assert "installation_id" in inspect.signature(get_installation_usage_summary).parameters
