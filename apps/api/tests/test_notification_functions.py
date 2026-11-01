"""Verify notification function signatures."""

import pytest
import inspect
from app.services import app_notifications

FUNCS = [
    name for name, obj in inspect.getmembers(app_notifications)
    if inspect.iscoroutinefunction(obj) and name.startswith("notify_")
]

@pytest.mark.parametrize("fn_name", FUNCS)
def test_is_async(fn_name):
    fn = getattr(app_notifications, fn_name)
    assert inspect.iscoroutinefunction(fn)

@pytest.mark.parametrize("fn_name", FUNCS)
def test_has_db_param(fn_name):
    fn = getattr(app_notifications, fn_name)
    sig = inspect.signature(fn)
    assert "db" in sig.parameters

@pytest.mark.parametrize("fn_name", FUNCS)
def test_has_app_id_or_name(fn_name):
    fn = getattr(app_notifications, fn_name)
    sig = inspect.signature(fn)
    params = set(sig.parameters.keys())
    assert "app_name" in params or "app_id" in params

def test_notification_count():
    assert len(FUNCS) == 6
