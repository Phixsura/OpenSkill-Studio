"""API deps — app auth helpers."""

import inspect
import pytest
from app.api.deps import require_app_scopes, get_current_user_or_app, _authenticate_api_key


def test_require_app_scopes_returns_callable():
    dep = require_app_scopes("read:cohorts", "write:cohorts")
    assert callable(dep)

def test_require_app_scopes_single():
    dep = require_app_scopes("read:cohorts")
    assert callable(dep)

def test_get_current_user_or_app_is_async():
    assert inspect.iscoroutinefunction(get_current_user_or_app)

def test_authenticate_api_key_is_async():
    assert inspect.iscoroutinefunction(_authenticate_api_key)

def test_get_current_user_or_app_params():
    params = inspect.signature(get_current_user_or_app).parameters
    assert "request" in params or "authorization" in params or len(params) >= 1

def test_authenticate_api_key_params():
    params = inspect.signature(_authenticate_api_key).parameters
    assert "key" in params or "api_key" in params or "token" in params or len(params) >= 1
