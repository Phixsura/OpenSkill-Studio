"""Adapter SDK — base classes, capabilities, registration."""

import pytest
from dataclasses import fields
from app.services.adapter_sdk import (
    Capability, HealthCheck, AdapterMetadata, ProviderAdapterSDK,
    SourceRecord, EcosystemSourceAdapter, register_adapter,
)

# --- dataclass field checks ---

DATACLASS_FIELDS = [
    (Capability, {"name", "description"}),
    (HealthCheck, {"healthy", "message"}),
    (SourceRecord, {"id", "source", "data"}),
]

@pytest.mark.parametrize("cls,expected_fields", DATACLASS_FIELDS, ids=lambda x: x.__name__ if hasattr(x, '__name__') else str(x))
def test_dataclass_fields(cls, expected_fields):
    actual = {f.name for f in fields(cls)}
    assert expected_fields.issubset(actual)

# --- AdapterMetadata ---

def test_adapter_metadata_fields():
    actual = {f.name for f in fields(AdapterMetadata)}
    assert {"name", "version", "description", "capabilities"}.issubset(actual)

# --- ABC method checks ---

ABC_METHODS = [
    (ProviderAdapterSDK, ["execute", "health_check", "validate_config", "validate_credentials", "get_metadata", "supports_capability"]),
    (EcosystemSourceAdapter, ["fetch_records", "validate_config", "health_check", "get_metadata"]),
]

@pytest.mark.parametrize("cls,methods", ABC_METHODS, ids=lambda x: x.__name__ if hasattr(x, '__name__') else str(x))
def test_abc_has_methods(cls, methods):
    for method in methods:
        assert hasattr(cls, method), f"{cls.__name__} missing {method}"

def test_provider_adapter_is_abstract():
    with pytest.raises(TypeError):
        ProviderAdapterSDK()

def test_ecosystem_adapter_is_abstract():
    with pytest.raises(TypeError):
        EcosystemSourceAdapter()

def test_register_adapter_callable():
    assert callable(register_adapter)
