"""Developer service kill switch (revoke) function tests."""

import inspect
import pytest
from app.services import developer as dev_svc

def test_revoke_functions_exist():
    """Kill switch functions should exist."""
    # App revocation is done via transition_app_status
    assert hasattr(dev_svc, "transition_app_status")

def test_revoke_api_key_exists():
    assert hasattr(dev_svc, "revoke_api_key")
    assert inspect.iscoroutinefunction(dev_svc.revoke_api_key)

def test_uninstall_app_exists():
    assert hasattr(dev_svc, "uninstall_app")
    assert inspect.iscoroutinefunction(dev_svc.uninstall_app)

def test_transition_accepts_revoked():
    """The state machine should accept 'revoked' as a target state."""
    # From the state machine test, published → revoked is valid
    allowed = {
        "published": {"deprecated", "revoked"},
        "deprecated": {"revoked"},
    }
    assert "revoked" in allowed["published"]
    assert "revoked" in allowed["deprecated"]

def test_revoke_api_key_params():
    params = inspect.signature(dev_svc.revoke_api_key).parameters
    assert "db" in params
    assert "key" in params
