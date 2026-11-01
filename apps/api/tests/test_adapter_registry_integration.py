"""Integration tests for adapter and source registry with registered adapters."""

import uuid

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.services.adapter_sdk import (
    Capability,
    EcosystemSourceAdapter,
    HealthCheck,
    ProviderAdapterSDK,
    SourceRecord,
    register_adapter,
    register_source,
    get_adapter,
    get_source,
    list_adapters,
    list_sources,
)


# ── Test adapters ────────────────────────────────────────


class IntegrationVideoAdapter(ProviderAdapterSDK):
    name = "intg-video-adapter"
    display_name = "Integration Video"
    version = "2.0.0"
    capabilities = [
        Capability(key="text_to_video", input_schema={"prompt": "string"}, pricing={"unit": "second", "cost": 0.05}),
        Capability(key="image_to_video", input_schema={"image_url": "string"}),
    ]

    async def execute(self, capability, inputs, config, credentials, *, idempotency_key=""):
        return {"url": f"https://video.test/{idempotency_key}", "__usage__": [{"type": "seconds", "qty": 10}]}

    async def health_check(self):
        return HealthCheck(status="healthy", latency_ms=25, message="All good")


class IntegrationTalentSource(EcosystemSourceAdapter):
    name = "intg-talent-source"
    source_type = "talent_directory"
    version = "1.5.0"
    ingestion_rate_limit = 2000

    async def fetch_records(self, config, credentials, *, since=None, limit=100):
        return [
            SourceRecord(external_id=f"t-{i}", data={"name": f"Person {i}"}, source_type="talent_directory")
            for i in range(min(limit, 5))
        ]


# ── Registration ─────────────────────────────────────────


def test_register_and_retrieve_adapter():
    adapter = IntegrationVideoAdapter()
    register_adapter(adapter)
    retrieved = get_adapter("intg-video-adapter")
    assert retrieved is adapter
    assert retrieved.display_name == "Integration Video"


def test_register_and_retrieve_source():
    source = IntegrationTalentSource()
    register_source(source)
    retrieved = get_source("intg-talent-source")
    assert retrieved is source
    assert retrieved.ingestion_rate_limit == 2000


def test_list_registered_adapters():
    register_adapter(IntegrationVideoAdapter())
    adapters = list_adapters()
    names = [a.name for a in adapters]
    assert "intg-video-adapter" in names


def test_list_registered_sources():
    register_source(IntegrationTalentSource())
    sources = list_sources()
    names = [s["name"] for s in sources]
    assert "intg-talent-source" in names


# ── Adapter execution ────────────────────────────────────


@pytest.mark.asyncio
async def test_adapter_execute():
    adapter = IntegrationVideoAdapter()
    result = await adapter.execute("text_to_video", {"prompt": "test"}, {}, {"KEY": "val"}, idempotency_key="idem-1")
    assert "url" in result
    assert "__usage__" in result


@pytest.mark.asyncio
async def test_adapter_health():
    adapter = IntegrationVideoAdapter()
    health = await adapter.health_check()
    assert health.status == "healthy"
    assert health.latency_ms == 25


@pytest.mark.asyncio
async def test_adapter_metadata():
    adapter = IntegrationVideoAdapter()
    meta = adapter.get_metadata()
    assert meta.name == "intg-video-adapter"
    assert meta.version == "2.0.0"
    assert len(meta.capabilities) == 2
    assert meta.health_check_supported is True
    assert meta.idempotent is True


@pytest.mark.asyncio
async def test_adapter_supports_capability():
    adapter = IntegrationVideoAdapter()
    assert adapter.supports_capability("text_to_video")
    assert adapter.supports_capability("image_to_video")
    assert not adapter.supports_capability("audio_generation")


# ── Source execution ─────────────────────────────────────


@pytest.mark.asyncio
async def test_source_fetch():
    source = IntegrationTalentSource()
    records = await source.fetch_records({}, {}, limit=3)
    assert len(records) == 3
    assert records[0].external_id == "t-0"
    assert records[0].checksum  # auto-computed


@pytest.mark.asyncio
async def test_source_metadata():
    source = IntegrationTalentSource()
    meta = source.get_metadata()
    assert meta["name"] == "intg-talent-source"
    assert meta["source_type"] == "talent_directory"
    assert meta["ingestion_rate_limit"] == 2000


@pytest.mark.asyncio
async def test_source_health():
    source = IntegrationTalentSource()
    health = await source.health_check()
    assert health.status == "healthy"


# ── API endpoints ────────────────────────────────────────


def _email():
    return f"areg-{uuid.uuid4().hex[:8]}@test.com"


@pytest_asyncio.fixture
async def c():
    from app.main import app
    orig = app.router.lifespan_context
    from contextlib import asynccontextmanager
    from app.core.database import engine

    @asynccontextmanager
    async def _noop(a):
        yield

    app.router.lifespan_context = _noop
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.router.lifespan_context = orig
    await engine.dispose()


@pytest.mark.asyncio
async def test_adapters_endpoint(c):
    r = await c.post("/api/v1/auth/register", json={"email": _email(), "password": "TestPass123!", "display_name": "AR"})
    h = {"Authorization": f"Bearer {r.json()['access_token']}"}
    register_adapter(IntegrationVideoAdapter())
    r = await c.get("/api/v1/developer/adapters", headers=h)
    assert r.status_code == 200
    assert isinstance(r.json()["data"], list)


@pytest.mark.asyncio
async def test_sources_endpoint(c):
    r = await c.post("/api/v1/auth/register", json={"email": _email(), "password": "TestPass123!", "display_name": "AR"})
    h = {"Authorization": f"Bearer {r.json()['access_token']}"}
    register_source(IntegrationTalentSource())
    r = await c.get("/api/v1/developer/sources", headers=h)
    assert r.status_code == 200
    assert isinstance(r.json()["data"], list)
