"""Conformance check functions exist and have correct signatures."""

import inspect
import pytest
from app.services import conformance

CHECK_FUNCS = [
    ("_check_manifest", True),
    ("_check_versions", True),
    ("_check_installations", True),
    ("_check_sandbox_health", True),
    ("_check_api_keys", True),
    ("_check_event_subscriptions", True),
    ("_check_security", False),  # sync
]

@pytest.mark.parametrize("name,is_async", CHECK_FUNCS, ids=lambda x: x if isinstance(x, str) else str(x))
def test_check_exists(name, is_async):
    assert hasattr(conformance, name)

@pytest.mark.parametrize("name,is_async", CHECK_FUNCS, ids=lambda x: x if isinstance(x, str) else str(x))
def test_check_async_status(name, is_async):
    func = getattr(conformance, name)
    if is_async:
        assert inspect.iscoroutinefunction(func)
    else:
        assert not inspect.iscoroutinefunction(func)

def test_run_conformance_checks_is_async():
    assert inspect.iscoroutinefunction(conformance.run_conformance_checks)

def test_total_check_functions():
    assert len(CHECK_FUNCS) == 7
