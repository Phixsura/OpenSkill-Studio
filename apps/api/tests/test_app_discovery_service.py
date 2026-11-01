"""App discovery service tests."""

import inspect
import pytest
from app.services.app_discovery import get_featured_apps, get_recent_apps, get_trending_apps


DISCOVERY_FUNCS = [get_featured_apps, get_recent_apps, get_trending_apps]

@pytest.mark.parametrize("func", DISCOVERY_FUNCS, ids=lambda f: f.__name__)
def test_all_async(func):
    assert inspect.iscoroutinefunction(func)

@pytest.mark.parametrize("func", DISCOVERY_FUNCS, ids=lambda f: f.__name__)
def test_requires_db_session(func):
    sig = inspect.signature(func)
    assert "db" in sig.parameters

@pytest.mark.parametrize("func", DISCOVERY_FUNCS, ids=lambda f: f.__name__)
def test_has_limit_param(func):
    sig = inspect.signature(func)
    assert "limit" in sig.parameters

def test_featured_default_limit():
    sig = inspect.signature(get_featured_apps)
    assert sig.parameters["limit"].default in (6, 8, 10, 12)

def test_recent_default_limit():
    sig = inspect.signature(get_recent_apps)
    assert sig.parameters["limit"].default in (10, 12, 20)

def test_trending_default_limit():
    sig = inspect.signature(get_trending_apps)
    assert sig.parameters["limit"].default in (10, 12, 20)
