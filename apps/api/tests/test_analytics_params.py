"""App analytics function parameter tests."""

import inspect
import pytest
from app.services.app_analytics import (
    get_install_timeline, get_execution_timeline,
    get_top_orgs, get_app_summary_metrics,
)

TIMELINE_FUNCS = [get_install_timeline, get_execution_timeline]

@pytest.mark.parametrize("func", TIMELINE_FUNCS, ids=lambda f: f.__name__)
def test_timeline_has_days(func):
    default = inspect.signature(func).parameters["days"].default
    assert isinstance(default, int) and default > 0

@pytest.mark.parametrize("func", TIMELINE_FUNCS, ids=lambda f: f.__name__)
def test_timeline_return_hint(func):
    assert "return" in inspect.get_annotations(func)

def test_top_orgs_default_limit():
    default = inspect.signature(get_top_orgs).parameters["limit"].default
    assert isinstance(default, int) and default > 0

def test_summary_metrics_return_hint():
    assert "return" in inspect.get_annotations(get_app_summary_metrics)
