from app.services.app_marketplace_extension_api_usage_billing import (
    ApiUsageBillingService, PricingTier,
)


def test_record_usage():
    svc = ApiUsageBillingService()
    svc.record_usage("ext-1", "/api/data", 100, 5000)
    svc.record_usage("ext-1", "/api/data", 50, 2500)
    usage = svc.get_usage("ext-1")
    assert usage["total_calls"] == 150
    assert usage["total_bytes"] == 7500


def test_free_tier():
    svc = ApiUsageBillingService()
    cost = svc.calculate_cost(5000)  # within free tier
    assert cost == 0


def test_paid_tier():
    svc = ApiUsageBillingService()
    cost = svc.calculate_cost(15000)  # 10k free + 5k at 0.01
    assert cost == 50  # 5000 * 0.01


def test_multiple_tiers():
    svc = ApiUsageBillingService()
    cost = svc.calculate_cost(150000)  # 10k free + 90k at 0.01 + 50k at 0.005
    assert cost == 1200  # 10k free + 100k*0.01 + 40k*0.005


def test_generate_invoice():
    svc = ApiUsageBillingService()
    svc.record_usage("ext-1", "/api/data", 20000)
    svc.record_usage("ext-1", "/api/search", 5000)
    invoice = svc.generate_invoice("ext-1", "2024-01-01", "2024-01-31")
    assert invoice.total_calls == 25000
    assert invoice.total_cost_cents > 0
    assert len(invoice.line_items) == 2


def test_reset_usage():
    svc = ApiUsageBillingService()
    svc.record_usage("ext-1", "/api/data", 100)
    svc.reset_usage("ext-1")
    usage = svc.get_usage("ext-1")
    assert usage["total_calls"] == 0


def test_custom_tiers():
    tiers = [PricingTier(up_to=100, price_per_call_cents=0.0),
             PricingTier(up_to=0, price_per_call_cents=1.0)]
    svc = ApiUsageBillingService(tiers=tiers)
    cost = svc.calculate_cost(200)
    assert cost == 100  # 100 free + 100 at 1.0


def test_invoice_history():
    svc = ApiUsageBillingService()
    svc.record_usage("ext-1", "/api", 100)
    svc.generate_invoice("ext-1", "2024-01", "2024-01")
    svc.generate_invoice("ext-1", "2024-02", "2024-02")
    assert len(svc.get_invoices("ext-1")) == 2
