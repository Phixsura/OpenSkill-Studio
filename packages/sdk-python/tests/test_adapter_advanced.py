"""Advanced adapter and source tests for Python SDK."""

import pytest

from openskill_sdk import Capability, EcosystemSourceAdapter, HealthCheck, ProviderAdapter, SourceRecord


class MultiCapAdapter(ProviderAdapter):
    name = "multi-cap"
    display_name = "Multi Capability"
    version = "3.0.0"
    capabilities = [
        Capability(key="text_gen", pricing={"unit": "token", "cost": 0.001}),
        Capability(key="image_gen", pricing={"unit": "image", "cost": 0.02}),
        Capability(key="audio_gen"),
    ]
    retry_policy = {"max_attempts": 5, "backoff": "linear"}
    idempotent = False

    async def execute(self, capability, inputs, config, credentials, *, idempotency_key=""):
        return {"capability": capability, "done": True}

    async def health_check(self):
        return HealthCheck(status="degraded", latency_ms=500, message="High load")

    async def validate_config(self, config):
        errors = []
        if "base_url" not in config:
            errors.append("base_url required")
        return errors

    async def validate_credentials(self, credentials):
        return "api_key" in credentials


class PaginatedSource(EcosystemSourceAdapter):
    name = "paginated-source"
    source_type = "job_board"
    version = "2.0.0"
    provenance_tracking = False
    ingestion_rate_limit = 500

    async def fetch_records(self, config, credentials, *, since=None, limit=100):
        start = int(since) if since else 0
        return [
            SourceRecord(external_id=f"job-{start + i}", data={"title": f"Job {start + i}"}, source_type="job_board")
            for i in range(min(limit, 3))
        ]

    async def validate_config(self, config):
        if "feed_url" not in config:
            return ["feed_url required"]
        return []


# ── Multi-capability adapter ─────────────────────────────


def test_multi_capabilities():
    a = MultiCapAdapter()
    assert len(a.capabilities) == 3
    assert a.supports_capability("text_gen")
    assert a.supports_capability("image_gen")
    assert a.supports_capability("audio_gen")
    assert not a.supports_capability("video_gen")


def test_retry_and_idempotency():
    a = MultiCapAdapter()
    assert a.retry_policy["max_attempts"] == 5
    assert a.idempotent is False


@pytest.mark.asyncio
async def test_multi_execute():
    a = MultiCapAdapter()
    r = await a.execute("text_gen", {"prompt": "test"}, {}, {"api_key": "k"})
    assert r["capability"] == "text_gen"
    assert r["done"] is True


@pytest.mark.asyncio
async def test_degraded_health():
    a = MultiCapAdapter()
    h = await a.health_check()
    assert h.status == "degraded"
    assert h.latency_ms == 500


@pytest.mark.asyncio
async def test_config_validation_fails():
    a = MultiCapAdapter()
    errors = await a.validate_config({})
    assert "base_url required" in errors


@pytest.mark.asyncio
async def test_config_validation_passes():
    a = MultiCapAdapter()
    errors = await a.validate_config({"base_url": "https://api.test"})
    assert errors == []


@pytest.mark.asyncio
async def test_credential_validation():
    a = MultiCapAdapter()
    assert await a.validate_credentials({"api_key": "test"}) is True
    assert await a.validate_credentials({}) is False


# ── Paginated source ────────────────────────────────────


@pytest.mark.asyncio
async def test_paginated_fetch():
    s = PaginatedSource()
    page1 = await s.fetch_records({}, {}, limit=3)
    assert len(page1) == 3
    assert page1[0].external_id == "job-0"

    page2 = await s.fetch_records({}, {}, since="3", limit=3)
    assert page2[0].external_id == "job-3"


@pytest.mark.asyncio
async def test_source_config_validation():
    s = PaginatedSource()
    assert await s.validate_config({}) == ["feed_url required"]
    assert await s.validate_config({"feed_url": "https://jobs.test/feed"}) == []


def test_source_provenance_disabled():
    s = PaginatedSource()
    assert s.provenance_tracking is False
    assert s.ingestion_rate_limit == 500


def test_source_record_auto_checksum():
    r1 = SourceRecord(external_id="x", data={"a": 1, "b": 2}, source_type="test")
    r2 = SourceRecord(external_id="y", data={"a": 1, "b": 2}, source_type="test")
    r3 = SourceRecord(external_id="z", data={"a": 1, "b": 3}, source_type="test")
    assert r1.checksum == r2.checksum
    assert r1.checksum != r3.checksum
    assert r1.fetched_at  # auto-generated
