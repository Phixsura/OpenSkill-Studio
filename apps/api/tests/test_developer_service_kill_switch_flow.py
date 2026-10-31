"""Kill switch flow — verify revoke path exists for all entities."""

import inspect
import pytest
from app.services import developer as dev_svc

REVOKE_FUNCTIONS = [
    ("transition_app_status", "Revoke app"),
    ("revoke_api_key", "Revoke API key"),
    ("uninstall_app", "Uninstall"),
    ("delete_automation_rule", "Delete rule"),
    ("delete_secret", "Delete secret"),
]

@pytest.mark.parametrize("func_name,desc", REVOKE_FUNCTIONS, ids=lambda x: str(x)[:20])
def test_revoke_function_exists(func_name, desc):
    assert hasattr(dev_svc, func_name)

@pytest.mark.parametrize("func_name,desc", REVOKE_FUNCTIONS, ids=lambda x: str(x)[:20])
def test_revoke_is_async(func_name, desc):
    assert inspect.iscoroutinefunction(getattr(dev_svc, func_name))

@pytest.mark.parametrize("func_name,desc", REVOKE_FUNCTIONS, ids=lambda x: str(x)[:20])
def test_revoke_needs_db(func_name, desc):
    assert "db" in inspect.signature(getattr(dev_svc, func_name)).parameters
