"""Python SDK client tests."""

import inspect
import pytest
from openskill_sdk.client import OpenSkillClient


def test_init_defaults():
    c = OpenSkillClient(api_key="test_key")
    assert c._api_key == "test_key"

def test_init_custom_base_url():
    c = OpenSkillClient(api_key="k", base_url="https://custom.api.com")
    assert "custom.api.com" in c._base_url

def test_has_http_methods():
    for method in ["get", "post", "patch", "delete"]:
        assert hasattr(OpenSkillClient, method)
        assert inspect.iscoroutinefunction(getattr(OpenSkillClient, method))

def test_is_context_manager():
    assert hasattr(OpenSkillClient, "__aenter__")
    assert hasattr(OpenSkillClient, "__aexit__")

def test_request_is_async():
    assert inspect.iscoroutinefunction(OpenSkillClient.request)

def test_close_is_async():
    assert inspect.iscoroutinefunction(OpenSkillClient.close)

def test_has_developer_resource():
    c = OpenSkillClient(api_key="k")
    assert hasattr(c, "developers") or hasattr(c, "developer")

def test_has_apps_resource():
    c = OpenSkillClient(api_key="k")
    assert hasattr(c, "apps") or hasattr(c, "app")
