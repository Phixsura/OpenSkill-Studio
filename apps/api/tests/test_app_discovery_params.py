"""App discovery function parameter defaults."""

import inspect
import pytest
from app.services.app_discovery import get_featured_apps, get_recent_apps, get_trending_apps

def test_featured_default_limit():
    default = inspect.signature(get_featured_apps).parameters["limit"].default
    assert isinstance(default, int) and default > 0

def test_recent_default_limit():
    default = inspect.signature(get_recent_apps).parameters["limit"].default
    assert isinstance(default, int) and default > 0

def test_trending_default_limit():
    default = inspect.signature(get_trending_apps).parameters["limit"].default
    assert isinstance(default, int) and default > 0

def test_featured_limit_reasonable():
    default = inspect.signature(get_featured_apps).parameters["limit"].default
    assert 1 <= default <= 50

def test_recent_limit_reasonable():
    default = inspect.signature(get_recent_apps).parameters["limit"].default
    assert 1 <= default <= 100

def test_trending_limit_reasonable():
    default = inspect.signature(get_trending_apps).parameters["limit"].default
    assert 1 <= default <= 100
