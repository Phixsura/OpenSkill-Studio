import pytest
from datetime import datetime
from app.services.app_api_developer_platform_sdk_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_provider_integration_status import (
    AppAPIDeveloperPlatformSDKConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiProviderIntegrationStatus, ProviderStatus,
)

class TestProviderIntegrationStatus:
    def _now(self):
        return datetime(2026, 6, 1)

    def test_register_and_overview(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiProviderIntegrationStatus()
        svc.register("inst-1", ProviderStatus(provider_id="stripe", name="Stripe", status="operational", latency_ms=50))
        svc.register("inst-1", ProviderStatus(provider_id="twilio", name="Twilio", status="operational", latency_ms=80))
        overview = svc.get_overview("inst-1")
        assert overview.total_providers == 2 and overview.overall_status == "operational"

    def test_outage_overall(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiProviderIntegrationStatus()
        svc.register("inst-1", ProviderStatus(provider_id="p1", name="A", status="operational"))
        svc.register("inst-1", ProviderStatus(provider_id="p2", name="B", status="outage"))
        assert svc.get_overview("inst-1").overall_status == "outage"

    def test_update_status(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiProviderIntegrationStatus()
        svc.register("inst-1", ProviderStatus(provider_id="p1", name="A"))
        svc.update_status("inst-1", "p1", "degraded", latency_ms=500, error="Slow responses", now=self._now())
        providers = svc.list_providers("inst-1")
        assert providers[0].status == "degraded" and providers[0].error_message == "Slow responses"

    def test_sorted_by_severity(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiProviderIntegrationStatus()
        svc.register("inst-1", ProviderStatus(provider_id="p1", name="Good", status="operational"))
        svc.register("inst-1", ProviderStatus(provider_id="p2", name="Bad", status="outage"))
        providers = svc.list_providers("inst-1")
        assert providers[0].status == "outage"

    def test_invalid_status(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiProviderIntegrationStatus()
        with pytest.raises(ValueError, match="Invalid status"):
            svc.register("inst-1", ProviderStatus(provider_id="p1", name="X", status="broken"))

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiProviderIntegrationStatus()
        svc.register("inst-1", ProviderStatus(provider_id="p1", name="X"))
        assert svc.get_overview("inst-2").total_providers == 0
