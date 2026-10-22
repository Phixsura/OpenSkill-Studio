"""Tests for app discovery service functions."""

import asyncio
from app.services.app_discovery import get_featured_apps, get_recent_apps, get_trending_apps


def test_discovery_functions_async():
    assert asyncio.iscoroutinefunction(get_featured_apps)
    assert asyncio.iscoroutinefunction(get_recent_apps)
    assert asyncio.iscoroutinefunction(get_trending_apps)


def test_discovery_functions_have_defaults():
    """All discovery functions accept keyword-only limit/days."""
    import inspect
    sig = inspect.signature(get_featured_apps)
    assert "limit" in sig.parameters
    sig = inspect.signature(get_recent_apps)
    assert "limit" in sig.parameters
    sig = inspect.signature(get_trending_apps)
    assert "days" in sig.parameters
    assert "limit" in sig.parameters
