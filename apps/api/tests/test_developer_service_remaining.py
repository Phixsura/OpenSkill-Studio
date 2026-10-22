"""Developer service — remaining CRUD function signatures."""

import inspect
import pytest
from app.services import developer as dev_svc

REMAINING_FUNCS = [
    "create_automation_rule", "list_automation_rules", "get_automation_rule",
    "update_automation_rule", "delete_automation_rule",
    "set_secret", "get_decrypted_secrets", "list_secret_metadata", "delete_secret",
    "register_signing_key", "list_signing_keys",
]

@pytest.mark.parametrize("name", REMAINING_FUNCS)
def test_exists(name):
    assert hasattr(dev_svc, name)

@pytest.mark.parametrize("name", REMAINING_FUNCS)
def test_is_async(name):
    assert inspect.iscoroutinefunction(getattr(dev_svc, name))

@pytest.mark.parametrize("name", REMAINING_FUNCS)
def test_requires_db(name):
    assert "db" in inspect.signature(getattr(dev_svc, name)).parameters

# Verify key params
def test_set_secret_params():
    params = inspect.signature(dev_svc.set_secret).parameters
    assert "installation_id" in params
    assert "key" in params

def test_delete_secret_params():
    params = inspect.signature(dev_svc.delete_secret).parameters
    assert "installation_id" in params
    assert "key" in params

def test_register_signing_key_params():
    params = inspect.signature(dev_svc.register_signing_key).parameters
    assert "developer_id" in params
