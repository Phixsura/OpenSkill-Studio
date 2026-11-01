"""App analytics service tests."""

import inspect
import pytest
from app.services.app_analytics import (
    get_install_timeline, get_execution_timeline,
    get_top_orgs, get_app_summary_metrics,
)

FUNCS = [get_install_timeline, get_execution_timeline, get_top_orgs, get_app_summary_metrics]

@pytest.mark.parametrize("func", FUNCS, ids=lambda f: f.__name__)
def test_all_async(func):
    assert inspect.iscoroutinefunction(func)

@pytest.mark.parametrize("func", FUNCS, ids=lambda f: f.__name__)
def test_requires_db(func):
    assert "db" in inspect.signature(func).parameters

@pytest.mark.parametrize("func", FUNCS, ids=lambda f: f.__name__)
def test_requires_app_id(func):
    assert "app_id" in inspect.signature(func).parameters

TIMELINE_FUNCS = [get_install_timeline, get_execution_timeline]

@pytest.mark.parametrize("func", TIMELINE_FUNCS, ids=lambda f: f.__name__)
def test_timeline_has_days_param(func):
    assert "days" in inspect.signature(func).parameters

def test_top_orgs_has_limit():
    assert "limit" in inspect.signature(get_top_orgs).parameters
