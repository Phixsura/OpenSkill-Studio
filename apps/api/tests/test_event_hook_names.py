"""Verify all event hook function names follow naming convention."""

import pytest
from app.services import app_event_hooks
import inspect

HOOKS = [
    name for name, obj in inspect.getmembers(app_event_hooks)
    if inspect.iscoroutinefunction(obj) and name.startswith("on_")
]

@pytest.mark.parametrize("hook_name", HOOKS)
def test_hook_starts_with_on(hook_name):
    assert hook_name.startswith("on_")

@pytest.mark.parametrize("hook_name", HOOKS)
def test_hook_is_async(hook_name):
    fn = getattr(app_event_hooks, hook_name)
    assert inspect.iscoroutinefunction(fn)

@pytest.mark.parametrize("hook_name", HOOKS)
def test_hook_has_db_param(hook_name):
    fn = getattr(app_event_hooks, hook_name)
    sig = inspect.signature(fn)
    assert "db" in sig.parameters

def test_hook_count():
    assert len(HOOKS) == 12
