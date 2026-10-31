import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_consumer_tier_pricing import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerTierPricing, PricingTier,
)

class TestConsumerTierPricing:
    def test_create_and_assign(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerTierPricing()
        svc.create_tier("inst-1", PricingTier(tier_id="free", name="Free", monthly_limit=1000, price_per_request_cents=0.01))
        billing = svc.assign_tier("inst-1", "c1", "free")
        assert billing.tier_id == "free" and billing.usage_this_month == 0

    def test_overage_billing(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerTierPricing()
        svc.create_tier("inst-1", PricingTier(tier_id="starter", name="Starter", monthly_limit=100, price_per_request_cents=0.5, base_price_cents=999))
        svc.assign_tier("inst-1", "c1", "starter")
        svc.record_usage("inst-1", "c1", 150)
        inv = svc.get_invoice("inst-1", "c1")
        assert inv["usage"] == 150
        assert inv["overage_cents"] == 25.0  # 50 * 0.5
        assert inv["total_cents"] == 999 + 25.0

    def test_no_overage_under_limit(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerTierPricing()
        svc.create_tier("inst-1", PricingTier(tier_id="pro", name="Pro", monthly_limit=10000, price_per_request_cents=0.1))
        svc.assign_tier("inst-1", "c1", "pro")
        svc.record_usage("inst-1", "c1", 500)
        inv = svc.get_invoice("inst-1", "c1")
        assert inv["overage_cents"] == 0.0

    def test_bool_guard(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerTierPricing()
        svc.create_tier("inst-1", PricingTier(tier_id="t", name="T", monthly_limit=100, price_per_request_cents=0.1))
        svc.assign_tier("inst-1", "c1", "t")
        with pytest.raises(ValueError):
            svc.record_usage("inst-1", "c1", True)

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerTierPricing()
        svc.create_tier("inst-1", PricingTier(tier_id="t", name="T", monthly_limit=100, price_per_request_cents=0.1))
        assert len(svc.list_tiers("inst-2")) == 0
