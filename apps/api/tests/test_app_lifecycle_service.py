"""App lifecycle service tests."""

import inspect
import pytest
from app.services.app_lifecycle import (
    get_deprecation_info, auto_upgrade_installations,
    get_version_adoption, check_app_health,
)

FUNCS = [get_deprecation_info, auto_upgrade_installations, get_version_adoption, check_app_health]

@pytest.mark.parametrize("func", FUNCS, ids=lambda f: f.__name__)
def test_all_async(func):
    assert inspect.iscoroutinefunction(func)

@pytest.mark.parametrize("func", FUNCS, ids=lambda f: f.__name__)
def test_requires_db(func):
    assert "db" in inspect.signature(func).parameters

@pytest.mark.parametrize("func", FUNCS, ids=lambda f: f.__name__)
def test_requires_app_id(func):
    assert "app_id" in inspect.signature(func).parameters

def test_auto_upgrade_has_target_version():
    params = inspect.signature(auto_upgrade_installations).parameters
    assert "new_version_id" in params
