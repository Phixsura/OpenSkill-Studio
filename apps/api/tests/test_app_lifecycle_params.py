"""App lifecycle parameter tests."""

import inspect
import pytest
from app.services.app_lifecycle import (
    get_deprecation_info, auto_upgrade_installations,
    get_version_adoption, check_app_health,
)

def test_deprecation_return_hint():
    hints = inspect.get_annotations(get_deprecation_info)
    assert "return" in hints

def test_auto_upgrade_has_new_version_id():
    params = inspect.signature(auto_upgrade_installations).parameters
    assert "new_version_id" in params

def test_version_adoption_return_hint():
    hints = inspect.get_annotations(get_version_adoption)
    assert "return" in hints

def test_check_health_return_hint():
    hints = inspect.get_annotations(check_app_health)
    assert "return" in hints

def test_all_require_app_id():
    for f in [get_deprecation_info, auto_upgrade_installations, get_version_adoption, check_app_health]:
        assert "app_id" in inspect.signature(f).parameters
