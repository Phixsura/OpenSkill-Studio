"""Adapter SDK — base classes, capabilities, registration."""

import pytest
from dataclasses import fields
from app.services.adapter_sdk import (
    Capability, HealthCheck, AdapterMetadata, ProviderAdapterSDK,
    SourceRecord, EcosystemSourceAdapter, register_adapter,
)

DATACLASS_FIELDS = [
    (Capability, {"key", "input_schema", "output_schema"}),
    (HealthCheck, {"status", "latency_ms", "message"}),
    (SourceRecord, {"external_id", "data", "source_type"}),
    (AdapterMetadata, {"name", "version", "capabilities"}),
]

@pytest.mark.parametrize("cls,expected_fields", DATACLASS_FIELDS, ids=lambda x: x.__name__ if hasattr(x, '__name__') else str(x))
def test_dataclass_fields(cls, expected_fields):
    actual = {f.name for f in fields(cls)}
    assert expected_fields.issubset(actual)

ABC_METHODS = [
    (ProviderAdapterSDK, ["execute", "health_check", "validate_config", "validate_credentials", "get_metadata", "supports_capability"]),
    (EcosystemSourceAdapter, ["fetch_records", "validate_config", "health_check", "get_metadata"]),
]

@pytest.mark.parametrize("cls,methods", ABC_METHODS, ids=lambda x: x.__name__ if hasattr(x, '__name__') else str(x))
def test_abc_has_methods(cls, methods):
    for method in methods:
        assert hasattr(cls, method)

def test_provider_adapter_is_abstract():
    with pytest.raises(TypeError):
        ProviderAdapterSDK()

def test_ecosystem_adapter_is_abstract():
    with pytest.raises(TypeError):
        EcosystemSourceAdapter()

def test_register_adapter_callable():
    assert callable(register_adapter)
