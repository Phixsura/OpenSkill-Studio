import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_consumer_endpoint_consumer_api_consumer_api_usage_quota_dashboard import (
    AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointConsumerApiConsumerApiUsageQuotaDashboard, QuotaItem,
)

class TestUsageQuotaDashboard:
    def test_set_and_dashboard(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointConsumerApiConsumerApiUsageQuotaDashboard()
        svc.set_quota("inst-1", "c1", QuotaItem(name="API Requests", used=5000, limit=10000, category="requests"))
        svc.set_quota("inst-1", "c1", QuotaItem(name="Webhooks", used=8, limit=10, category="resources"))
        dashboard = svc.get_dashboard("inst-1", "c1")
        assert len(dashboard.items) == 2 and dashboard.items_at_risk == 1  # webhooks at 80%

    def test_exceeded(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointConsumerApiConsumerApiUsageQuotaDashboard()
        svc.set_quota("inst-1", "c1", QuotaItem(name="Storage", used=120, limit=100, category="storage"))
        dashboard = svc.get_dashboard("inst-1", "c1")
        assert dashboard.items_exceeded == 1

    def test_update_usage(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointConsumerApiConsumerApiUsageQuotaDashboard()
        svc.set_quota("inst-1", "c1", QuotaItem(name="Requests", used=0, limit=1000, category="requests"))
        svc.update_usage("inst-1", "c1", "Requests", 500)
        dashboard = svc.get_dashboard("inst-1", "c1")
        assert dashboard.items[0].used == 500

    def test_sorted_by_usage(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointConsumerApiConsumerApiUsageQuotaDashboard()
        svc.set_quota("inst-1", "c1", QuotaItem(name="Low", used=10, limit=1000, category="requests"))
        svc.set_quota("inst-1", "c1", QuotaItem(name="High", used=900, limit=1000, category="requests"))
        dashboard = svc.get_dashboard("inst-1", "c1")
        assert dashboard.items[0].name == "High"

    def test_invalid_category(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointConsumerApiConsumerApiUsageQuotaDashboard()
        with pytest.raises(ValueError, match="Invalid category"):
            svc.set_quota("inst-1", "c1", QuotaItem(name="X", used=0, limit=10, category="unknown"))

    def test_empty_dashboard(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointConsumerApiConsumerApiUsageQuotaDashboard()
        dashboard = svc.get_dashboard("inst-1", "c1")
        assert len(dashboard.items) == 0

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointConsumerApiConsumerApiUsageQuotaDashboard()
        svc.set_quota("inst-1", "c1", QuotaItem(name="X", used=5, limit=10, category="requests"))
        assert len(svc.get_dashboard("inst-2", "c1").items) == 0
