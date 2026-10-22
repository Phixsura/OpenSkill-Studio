"""Parametrized SourceRecord tests."""

import pytest
from app.services.adapter_sdk import SourceRecord

DATA_CASES = [
    {"a": 1},
    {"name": "Alice", "skills": ["python"]},
    {"nested": {"deep": {"value": 42}}},
    {},
    {"list": [1, 2, 3]},
]

@pytest.mark.parametrize("data", DATA_CASES)
def test_checksum_generated(data):
    r = SourceRecord(external_id="x", data=data, source_type="test")
    assert r.checksum
    assert len(r.checksum) == 16

@pytest.mark.parametrize("data", DATA_CASES)
def test_checksum_deterministic(data):
    r1 = SourceRecord(external_id="a", data=data, source_type="test")
    r2 = SourceRecord(external_id="b", data=data, source_type="test")
    assert r1.checksum == r2.checksum

@pytest.mark.parametrize("data", DATA_CASES)
def test_fetched_at_generated(data):
    r = SourceRecord(external_id="x", data=data, source_type="test")
    assert r.fetched_at
