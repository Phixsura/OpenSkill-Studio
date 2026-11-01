"""Adapter registry — register, get, list."""

import pytest
from app.services.adapter_sdk import (
    register_adapter, get_adapter, list_adapters,
    ProviderAdapterSDK, AdapterMetadata, HealthCheck,
)

class _RegTestAdapter(ProviderAdapterSDK):
    name = "reg-test-adapter"
    display_name = "Reg Test"
    version = "1.0.0"

    async def execute(self, cap, inputs, config, creds):
        return {}
    async def health_check(self):
        return HealthCheck(status="ok", latency_ms=1, message="ok", checked_at="now")
    async def validate_config(self, config):
        return []
    async def validate_credentials(self, creds):
        return True
    def get_metadata(self):
        return AdapterMetadata(name=self.name, display_name=self.display_name,
            version=self.version, capabilities=[], retry_policy={},
            idempotent=True, health_check_supported=True)
    def supports_capability(self, cap):
        return False

def test_register_and_get():
    a = _RegTestAdapter()
    register_adapter(a)
    found = get_adapter("reg-test-adapter")
    assert found is a

def test_get_missing():
    assert get_adapter("nonexistent-adapter-xyz") is None

def test_list_adapters():
    result = list_adapters()
    assert isinstance(result, list)
    names = [m.name for m in result]
    assert "reg-test-adapter" in names

def test_register_no_name_raises():
    class NoName(ProviderAdapterSDK):
        async def execute(self, *a): return {}
        async def health_check(self): return HealthCheck(status="ok", latency_ms=0, message="", checked_at="")
        async def validate_config(self, c): return []
        async def validate_credentials(self, c): return True
        def get_metadata(self): return AdapterMetadata(name="", display_name="", version="", capabilities=[], retry_policy={}, idempotent=True, health_check_supported=False)
        def supports_capability(self, c): return False
    with pytest.raises(ValueError):
        register_adapter(NoName())
