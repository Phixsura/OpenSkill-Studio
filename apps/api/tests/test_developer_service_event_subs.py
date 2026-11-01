"""Developer service — event subscription CRUD signatures."""

import inspect
import pytest
from app.services import developer as dev_svc

EVENT_SUB_FUNCS = [
    "create_event_subscription",
    "list_event_subscriptions", 
    "delete_event_subscription",
]

@pytest.mark.parametrize("name", EVENT_SUB_FUNCS)
def test_exists(name):
    assert hasattr(dev_svc, name)

@pytest.mark.parametrize("name", EVENT_SUB_FUNCS)
def test_is_async(name):
    assert inspect.iscoroutinefunction(getattr(dev_svc, name))

@pytest.mark.parametrize("name", EVENT_SUB_FUNCS)
def test_requires_db(name):
    assert "db" in inspect.signature(getattr(dev_svc, name)).parameters

def test_create_has_installation_id():
    params = inspect.signature(dev_svc.create_event_subscription).parameters
    assert "installation_id" in params

def test_list_has_installation_id():
    params = inspect.signature(dev_svc.list_event_subscriptions).parameters
    assert "installation_id" in params
