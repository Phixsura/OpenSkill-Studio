"""SourceRecord dataclass tests."""

import pytest
from dataclasses import fields
from app.services.adapter_sdk import SourceRecord

def test_has_external_id():
    assert "external_id" in {f.name for f in fields(SourceRecord)}

def test_has_data():
    assert "data" in {f.name for f in fields(SourceRecord)}

def test_has_source_type():
    assert "source_type" in {f.name for f in fields(SourceRecord)}

def test_has_fetched_at():
    assert "fetched_at" in {f.name for f in fields(SourceRecord)}

def test_has_checksum():
    assert "checksum" in {f.name for f in fields(SourceRecord)}

def test_instantiation():
    r = SourceRecord(external_id="ext-1", data={"name": "Test"}, source_type="api", fetched_at="2026-01-01", checksum="abc")
    assert r.external_id == "ext-1"
    assert r.data == {"name": "Test"}

def test_field_count():
    assert len(fields(SourceRecord)) >= 5
