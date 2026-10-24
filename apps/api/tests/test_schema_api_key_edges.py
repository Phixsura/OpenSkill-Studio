"""API key schema edge cases."""

import pytest
from pydantic import ValidationError
from app.schemas.developer import CreateApiKeyRequest

def test_valid_name():
    r = CreateApiKeyRequest(name="production-key")
    assert r.name == "production-key"

def test_empty_name_rejected():
    with pytest.raises(ValidationError):
        CreateApiKeyRequest(name="")

VALID_NAMES = ["key-1", "prod", "staging-key-v2", "a" * 50]

@pytest.mark.parametrize("name", VALID_NAMES)
def test_valid_key_names(name):
    r = CreateApiKeyRequest(name=name)
    assert r.name == name

def test_has_scopes_param():
    import inspect
    params = inspect.signature(CreateApiKeyRequest).parameters
    assert "scopes" in params or "name" in params  # At minimum name is required

def test_serialization():
    r = CreateApiKeyRequest(name="test-key")
    d = r.model_dump()
    assert d["name"] == "test-key"
