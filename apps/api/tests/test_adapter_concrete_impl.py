"""Adapter SDK — test concrete subclass implementation."""

import pytest
from app.services.adapter_sdk import (
    ProviderAdapterSDK, EcosystemSourceAdapter,
    AdapterMetadata, HealthCheck, Capability, SourceRecord,
    register_adapter,
)


class TestAdapter(ProviderAdapterSDK):
    name = "test-adapter"
    display_name = "Test Adapter"
    async def execute(self, capability, input_data, config, credentials):
        return {"result": "ok"}

    async def health_check(self) -> HealthCheck:
        return HealthCheck(status="healthy", latency_ms=10, message="ok", checked_at="now")

    async def validate_config(self, config):
        return []

    async def validate_credentials(self, credentials):
        return True

    def get_metadata(self) -> AdapterMetadata:
        return AdapterMetadata(
            name="test", display_name="Test", version="1.0.0",
            capabilities=[], retry_policy={}, idempotent=True,
            health_check_supported=True,
        )

    def supports_capability(self, capability):
        return True


class TestSource(EcosystemSourceAdapter):
    async def fetch_records(self, config, credentials, since=None):
        return [SourceRecord(external_id="1", data={}, source_type="test", fetched_at="now", checksum="abc")]

    async def validate_config(self, config):
        return []

    async def health_check(self):
        return HealthCheck(status="healthy", latency_ms=5, message="ok", checked_at="now")

    def get_metadata(self):
        return {"name": "test-source"}


def test_concrete_adapter_instantiates():
    a = TestAdapter()
    assert a is not None

def test_concrete_adapter_metadata():
    a = TestAdapter()
    m = a.get_metadata()
    assert m.name == "test"

def test_concrete_adapter_supports():
    a = TestAdapter()
    assert a.supports_capability("anything") is True

def test_concrete_source_instantiates():
    s = TestSource()
    assert s is not None

def test_register_adapter():
    a = TestAdapter()
    register_adapter(a)  # should not raise
