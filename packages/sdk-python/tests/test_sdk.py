"""Tests for the openskill-sdk Python package."""

import hashlib
import json

import pytest

from openskill_sdk import (
    ApiError,
    AuthError,
    Capability,
    EcosystemSourceAdapter,
    HealthCheck,
    NotFoundError,
    OpenSkillClient,
    OpenSkillError,
    ProviderAdapter,
    SourceRecord,
)


# ── Error hierarchy ──────────────────────────────────────


def test_error_hierarchy():
    assert issubclass(ApiError, OpenSkillError)
    assert issubclass(AuthError, OpenSkillError)
    assert issubclass(NotFoundError, OpenSkillError)


def test_api_error():
    err = ApiError("test error", "TEST_CODE", 400, ["detail1"])
    assert str(err) == "test error"
    assert err.code == "TEST_CODE"
    assert err.status_code == 400
    assert err.details == ["detail1"]


def test_auth_error_defaults():
    err = AuthError()
    assert err.status_code == 401
    assert err.code == "AUTH_ERROR"


def test_not_found_error_defaults():
    err = NotFoundError()
    assert err.status_code == 404


# ── Capability ───────────────────────────────────────────


def test_capability():
    cap = Capability(
        key="text_to_video",
        input_schema={"prompt": "string"},
        output_schema={"url": "string"},
        pricing={"unit": "second", "cost": 0.05},
    )
    assert cap.key == "text_to_video"
    assert cap.pricing["cost"] == 0.05


def test_capability_defaults():
    cap = Capability(key="test")
    assert cap.input_schema == {}
    assert cap.output_schema == {}
    assert cap.pricing == {}


# ── HealthCheck ──────────────────────────────────────────


def test_health_check():
    h = HealthCheck(status="healthy", latency_ms=42, message="OK")
    assert h.status == "healthy"
    assert h.latency_ms == 42
    assert h.checked_at  # auto-generated


# ── SourceRecord ─────────────────────────────────────────


def test_source_record_checksum():
    r1 = SourceRecord(external_id="1", data={"a": 1}, source_type="test")
    r2 = SourceRecord(external_id="2", data={"a": 1}, source_type="test")
    assert r1.checksum == r2.checksum  # same data = same checksum

    r3 = SourceRecord(external_id="3", data={"a": 2}, source_type="test")
    assert r1.checksum != r3.checksum  # different data


def test_source_record_custom_checksum():
    r = SourceRecord(external_id="1", data={}, source_type="test", checksum="custom")
    assert r.checksum == "custom"


# ── ProviderAdapter ──────────────────────────────────────


class TestAdapter(ProviderAdapter):
    name = "test-adapter"
    display_name = "Test"
    capabilities = [Capability(key="test_cap")]

    async def execute(self, capability, inputs, config, credentials, *, idempotency_key=""):
        return {"result": "ok"}


def test_adapter_supports_capability():
    adapter = TestAdapter()
    assert adapter.supports_capability("test_cap") is True
    assert adapter.supports_capability("other") is False


@pytest.mark.asyncio
async def test_adapter_execute():
    adapter = TestAdapter()
    result = await adapter.execute("test_cap", {}, {}, {})
    assert result["result"] == "ok"


@pytest.mark.asyncio
async def test_adapter_default_health():
    adapter = TestAdapter()
    health = await adapter.health_check()
    assert health.status == "healthy"


@pytest.mark.asyncio
async def test_adapter_default_validate():
    adapter = TestAdapter()
    errors = await adapter.validate_config({"key": "val"})
    assert errors == []
    assert await adapter.validate_credentials({"K": "V"}) is True


# ── EcosystemSourceAdapter ───────────────────────────────


class TestSource(EcosystemSourceAdapter):
    name = "test-source"
    source_type = "test_db"

    async def fetch_records(self, config, credentials, *, since=None, limit=100):
        return [SourceRecord(external_id="r1", data={"x": 1}, source_type="test_db")]


@pytest.mark.asyncio
async def test_source_fetch():
    src = TestSource()
    records = await src.fetch_records({}, {})
    assert len(records) == 1
    assert records[0].external_id == "r1"


@pytest.mark.asyncio
async def test_source_defaults():
    src = TestSource()
    assert src.provenance_tracking is True
    assert src.ingestion_rate_limit == 1000
    health = await src.health_check()
    assert health.status == "healthy"
    errors = await src.validate_config({})
    assert errors == []


# ── Client construction ──────────────────────────────────


def test_client_construction():
    client = OpenSkillClient.__new__(OpenSkillClient)
    # Just verify the class exists and can be referenced
    assert OpenSkillClient is not None


def test_version():
    from openskill_sdk import __version__

    assert __version__ == "0.1.0"
