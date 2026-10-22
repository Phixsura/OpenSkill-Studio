"""HealthCheck dataclass tests."""

import pytest
from dataclasses import fields
from app.services.adapter_sdk import HealthCheck

EXPECTED = ["status", "latency_ms", "message", "checked_at"]

@pytest.mark.parametrize("field", EXPECTED)
def test_field_exists(field):
    assert field in {f.name for f in fields(HealthCheck)}

def test_healthy():
    h = HealthCheck(status="healthy", latency_ms=5, message="ok", checked_at="now")
    assert h.status == "healthy"

def test_unhealthy():
    h = HealthCheck(status="unhealthy", latency_ms=5000, message="timeout", checked_at="now")
    assert h.status == "unhealthy"

def test_latency_numeric():
    h = HealthCheck(status="healthy", latency_ms=42, message="ok", checked_at="now")
    assert isinstance(h.latency_ms, (int, float))
