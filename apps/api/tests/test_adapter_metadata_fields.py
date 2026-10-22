"""AdapterMetadata field completeness."""

import pytest
from dataclasses import fields
from app.services.adapter_sdk import AdapterMetadata

EXPECTED_FIELDS = {
    "name": str,
    "display_name": str,
    "version": str,
    "capabilities": list,
    "retry_policy": dict,
    "idempotent": bool,
    "health_check_supported": bool,
}

@pytest.mark.parametrize("field_name", EXPECTED_FIELDS.keys())
def test_field_exists(field_name):
    field_names = {f.name for f in fields(AdapterMetadata)}
    assert field_name in field_names

def test_instantiation():
    m = AdapterMetadata(
        name="test", display_name="Test Adapter", version="1.0.0",
        capabilities=[], retry_policy={"max_attempts": 3},
        idempotent=True, health_check_supported=True,
    )
    assert m.name == "test"
    assert m.version == "1.0.0"
    assert m.idempotent is True

def test_field_count():
    assert len(fields(AdapterMetadata)) >= 7
