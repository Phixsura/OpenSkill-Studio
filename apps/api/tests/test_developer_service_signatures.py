"""Developer service — CRUD function signatures."""

import inspect
import pytest
from app.services import developer as dev_svc

CRUD_FUNCS = [
    "create_developer_account", "get_developer_account", "get_developer_account_by_user",
    "list_developer_accounts", "update_developer_account",
    "create_app", "get_app", "list_apps", "update_app", "transition_app_status",
    "create_app_version", "get_app_version", "list_app_versions", "review_app_version",
    "install_app", "get_installation", "list_installations", "uninstall_app",
    "create_api_key", "authenticate_api_key", "list_api_keys", "revoke_api_key",
    "create_event_subscription",
]

@pytest.mark.parametrize("name", CRUD_FUNCS)
def test_exists(name):
    assert hasattr(dev_svc, name)

@pytest.mark.parametrize("name", CRUD_FUNCS)
def test_is_async(name):
    assert inspect.iscoroutinefunction(getattr(dev_svc, name))

@pytest.mark.parametrize("name", CRUD_FUNCS)
def test_requires_db(name):
    assert "db" in inspect.signature(getattr(dev_svc, name)).parameters

def test_total_count():
    assert len(CRUD_FUNCS) == 23
