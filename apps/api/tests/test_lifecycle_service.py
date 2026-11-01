"""Tests for app lifecycle service functions."""

import pytest
from app.services.app_lifecycle import (
    auto_upgrade_installations,
    check_app_health,
    get_deprecation_info,
    get_version_adoption,
)
from app.services.app_discovery import get_featured_apps, get_recent_apps, get_trending_apps
from app.services.app_search import search_marketplace_apps
from app.services.app_export import export_app_config, export_installation_config
from app.services.app_import import validate_import_data, prepare_import_plan


def test_lifecycle_functions_async():
    import asyncio
    assert asyncio.iscoroutinefunction(auto_upgrade_installations)
    assert asyncio.iscoroutinefunction(check_app_health)
    assert asyncio.iscoroutinefunction(get_deprecation_info)
    assert asyncio.iscoroutinefunction(get_version_adoption)


def test_discovery_functions_async():
    import asyncio
    assert asyncio.iscoroutinefunction(get_featured_apps)
    assert asyncio.iscoroutinefunction(get_recent_apps)
    assert asyncio.iscoroutinefunction(get_trending_apps)


def test_search_function_async():
    import asyncio
    assert asyncio.iscoroutinefunction(search_marketplace_apps)


def test_export_functions_async():
    import asyncio
    assert asyncio.iscoroutinefunction(export_app_config)
    assert asyncio.iscoroutinefunction(export_installation_config)


def test_import_functions_sync():
    assert callable(validate_import_data)
    assert callable(prepare_import_plan)
