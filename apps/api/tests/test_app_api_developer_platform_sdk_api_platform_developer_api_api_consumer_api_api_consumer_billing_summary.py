from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_billing_summary import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerBillingSummary, BillingSummary,
)

class TestConsumerBillingSummary:
    def test_total_calculation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerBillingSummary()
        s = svc.create_summary("inst-1", BillingSummary(consumer_id="c1", period="2024-01", base_cost_cents=4999, usage_cost_cents=1000, overage_cost_cents=500, discount_cents=200))
        assert s.total_cents == 6299
        assert s.total_dollars == "$62.99"

    def test_total_revenue(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerBillingSummary()
        svc.create_summary("inst-1", BillingSummary(consumer_id="c1", period="2024-01", base_cost_cents=5000))
        svc.create_summary("inst-1", BillingSummary(consumer_id="c2", period="2024-01", base_cost_cents=3000))
        assert svc.total_revenue("inst-1", "2024-01") == 8000

    def test_top_spenders(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerBillingSummary()
        svc.create_summary("inst-1", BillingSummary(consumer_id="c1", period="2024-01", base_cost_cents=1000))
        svc.create_summary("inst-1", BillingSummary(consumer_id="c2", period="2024-01", base_cost_cents=9000))
        top = svc.top_spenders("inst-1", "2024-01", 1)
        assert top[0].consumer_id == "c2"

    def test_discount_floors_zero(self):
        s = BillingSummary(consumer_id="c1", period="2024-01", base_cost_cents=100, discount_cents=500)
        assert s.total_cents == 0

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerBillingSummary()
        svc.create_summary("inst-1", BillingSummary(consumer_id="c1", period="2024-01"))
        assert len(svc.list_summaries("inst-2")) == 0
