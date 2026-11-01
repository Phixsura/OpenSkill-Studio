"""Tests for adapter SDK, event dispatch, and sandbox execution."""

import pytest

from app.services.adapter_sdk import (
    Capability,
    EcosystemSourceAdapter,
    HealthCheck,
    ProviderAdapterSDK,
    SourceRecord,
    get_adapter,
    get_source,
    list_adapters,
    list_sources,
    register_adapter,
    register_source,
)
from app.services.event_dispatch import (
    CANONICAL_EVENTS,
    EventDispatcher,
    PlatformEvent,
)


# ── Sample adapters for testing ──────────────────────────


class TestVideoAdapter(ProviderAdapterSDK):
    name = "test-video"
    display_name = "Test Video Generator"
    version = "1.0.0"
    capabilities = [
        Capability(
            key="text_to_video",
            input_schema={"prompt": "string", "duration_seconds": "integer"},
            output_schema={"video_url": "string"},
            pricing={"unit": "second", "cost_per_unit": 0.05},
        ),
        Capability(
            key="image_to_video",
            input_schema={"image_url": "string"},
            output_schema={"video_url": "string"},
        ),
    ]

    async def execute(self, capability, inputs, config, credentials, *, idempotency_key=""):
        return {
            "video_url": f"https://test.example.com/videos/{idempotency_key or 'test'}.mp4",
            "capability": capability,
            "__usage__": [{"usage_type": "video_generation_seconds", "quantity": 10}],
        }

    async def health_check(self):
        return HealthCheck(status="healthy", latency_ms=42, message="Test adapter OK")


class TestTalentSource(EcosystemSourceAdapter):
    name = "test-talent-db"
    source_type = "talent_directory"
    version = "1.0.0"
    ingestion_rate_limit = 500

    async def fetch_records(self, config, credentials, *, since=None, limit=100):
        return [
            SourceRecord(
                external_id="talent-001",
                data={"name": "Alice", "skills": ["python", "ml"]},
                source_type="talent_directory",
            ),
            SourceRecord(
                external_id="talent-002",
                data={"name": "Bob", "skills": ["rust", "wasm"]},
                source_type="talent_directory",
            ),
        ]

    async def health_check(self):
        return HealthCheck(status="healthy", latency_ms=15)


# ── Provider Adapter SDK Tests ───────────────────────────


class TestProviderAdapterSDK:
    def test_adapter_metadata(self):
        adapter = TestVideoAdapter()
        meta = adapter.get_metadata()
        assert meta.name == "test-video"
        assert meta.display_name == "Test Video Generator"
        assert meta.version == "1.0.0"
        assert len(meta.capabilities) == 2
        assert meta.idempotent is True
        assert meta.health_check_supported is True

    def test_supports_capability(self):
        adapter = TestVideoAdapter()
        assert adapter.supports_capability("text_to_video") is True
        assert adapter.supports_capability("image_to_video") is True
        assert adapter.supports_capability("nonexistent") is False

    @pytest.mark.asyncio
    async def test_execute(self):
        adapter = TestVideoAdapter()
        result = await adapter.execute(
            "text_to_video",
            {"prompt": "test", "duration_seconds": 5},
            {},
            {"API_KEY": "test-key"},
            idempotency_key="idem-123",
        )
        assert "video_url" in result
        assert result["capability"] == "text_to_video"
        assert "__usage__" in result

    @pytest.mark.asyncio
    async def test_health_check(self):
        adapter = TestVideoAdapter()
        health = await adapter.health_check()
        assert health.status == "healthy"
        assert health.latency_ms == 42

    @pytest.mark.asyncio
    async def test_default_validate_config(self):
        adapter = TestVideoAdapter()
        errors = await adapter.validate_config({"base_url": "https://test.com"})
        assert errors == []

    @pytest.mark.asyncio
    async def test_default_validate_credentials(self):
        adapter = TestVideoAdapter()
        valid = await adapter.validate_credentials({"API_KEY": "test"})
        assert valid is True

    def test_register_and_get_adapter(self):
        adapter = TestVideoAdapter()
        register_adapter(adapter)
        retrieved = get_adapter("test-video")
        assert retrieved is adapter
        assert any(a.name == "test-video" for a in list_adapters())

    def test_register_requires_name(self):
        class NoNameAdapter(ProviderAdapterSDK):
            async def execute(self, *args, **kwargs):
                return {}

        with pytest.raises(ValueError, match="must have a name"):
            register_adapter(NoNameAdapter())


# ── Ecosystem Source Adapter Tests ───────────────────────


class TestEcosystemSourceAdapter:
    def test_source_metadata(self):
        source = TestTalentSource()
        meta = source.get_metadata()
        assert meta["name"] == "test-talent-db"
        assert meta["source_type"] == "talent_directory"
        assert meta["ingestion_rate_limit"] == 500

    @pytest.mark.asyncio
    async def test_fetch_records(self):
        source = TestTalentSource()
        records = await source.fetch_records({}, {"API_KEY": "test"})
        assert len(records) == 2
        assert records[0].external_id == "talent-001"
        assert records[0].checksum  # auto-computed
        assert records[1].data["name"] == "Bob"

    @pytest.mark.asyncio
    async def test_health_check(self):
        source = TestTalentSource()
        health = await source.health_check()
        assert health.status == "healthy"

    def test_register_and_get_source(self):
        source = TestTalentSource()
        register_source(source)
        retrieved = get_source("test-talent-db")
        assert retrieved is source
        assert any(s["name"] == "test-talent-db" for s in list_sources())

    def test_source_record_checksum(self):
        r1 = SourceRecord(
            external_id="id1",
            data={"a": 1, "b": 2},
            source_type="test",
        )
        r2 = SourceRecord(
            external_id="id2",
            data={"a": 1, "b": 2},
            source_type="test",
        )
        # Same data → same checksum
        assert r1.checksum == r2.checksum

        r3 = SourceRecord(
            external_id="id3",
            data={"a": 1, "b": 3},
            source_type="test",
        )
        # Different data → different checksum
        assert r1.checksum != r3.checksum


# ── Event Dispatch Tests ─────────────────────────────────


class TestEventDispatch:
    def test_canonical_events_defined(self):
        """Verify canonical events include all expected categories."""
        assert "submission.completed" in CANONICAL_EVENTS
        assert "pack.published" in CANONICAL_EVENTS
        assert "workflow.run_completed" in CANONICAL_EVENTS
        assert "talent.credential_issued" in CANONICAL_EVENTS
        assert "marketplace.purchase_completed" in CANONICAL_EVENTS
        assert "app.installed" in CANONICAL_EVENTS
        assert len(CANONICAL_EVENTS) >= 30

    def test_platform_event_creation(self):
        event = PlatformEvent(
            event_type="submission.completed",
            data={"submission_id": "sub-123", "grade": 85},
            org_id="org-001",
            user_id="user-001",
        )
        assert event.event_type == "submission.completed"
        assert event.event_id  # auto-generated
        assert event.timestamp
        d = event.to_dict()
        assert d["event_type"] == "submission.completed"
        assert d["data"]["grade"] == 85
        assert d["org_id"] == "org-001"

    def test_event_id_deterministic(self):
        """Same event data at same timestamp → same event_id."""
        ts = "2026-10-22T12:00:00Z"
        e1 = PlatformEvent("test.event", {"x": 1}, timestamp=ts)
        e2 = PlatformEvent("test.event", {"x": 1}, timestamp=ts)
        assert e1.event_id == e2.event_id

    def test_event_id_varies(self):
        """Different data → different event_id."""
        ts = "2026-10-22T12:00:00Z"
        e1 = PlatformEvent("test.event", {"x": 1}, timestamp=ts)
        e2 = PlatformEvent("test.event", {"x": 2}, timestamp=ts)
        assert e1.event_id != e2.event_id

    def test_filter_matching(self):
        dispatcher = EventDispatcher()

        # eq
        assert dispatcher._matches_filter(
            {"grade": 85}, {"field": "grade", "operator": "eq", "value": 85}
        )
        assert not dispatcher._matches_filter(
            {"grade": 85}, {"field": "grade", "operator": "eq", "value": 90}
        )

        # gte
        assert dispatcher._matches_filter(
            {"grade": 85}, {"field": "grade", "operator": "gte", "value": 70}
        )
        assert not dispatcher._matches_filter(
            {"grade": 60}, {"field": "grade", "operator": "gte", "value": 70}
        )

        # contains
        assert dispatcher._matches_filter(
            {"status": "completed"}, {"field": "status", "operator": "contains", "value": "complet"}
        )

        # nested path
        assert dispatcher._matches_filter(
            {"data": {"score": 95}},
            {"field": "data.score", "operator": "gte", "value": 90},
        )

        # in
        assert dispatcher._matches_filter(
            {"status": "active"},
            {"field": "status", "operator": "in", "value": ["active", "pending"]},
        )

    def test_flatten_dict(self):
        dispatcher = EventDispatcher()
        flat = dispatcher._flatten_dict({
            "event_type": "test",
            "data": {"user_id": "u1", "nested": {"value": 42}},
        })
        assert flat["event_type"] == "test"
        assert flat["data.user_id"] == "u1"
        assert flat["data.nested.value"] == "42"
