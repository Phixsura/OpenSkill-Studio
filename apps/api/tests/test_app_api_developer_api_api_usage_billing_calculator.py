from app.services.app_api_developer_api_api_usage_billing_calculator import AppAPIDeveloperAPIApiUsageBillingCalculator

class TestBillingCalculator:
    def test_create_invoice(self):
        c = AppAPIDeveloperAPIApiUsageBillingCalculator()
        inv = c.create_invoice("inst-1", "inv-1", "2025-01", [
            {"item_id": "api", "description": "API Calls", "quantity": 100000, "unit_price_cents": 1},
            {"item_id": "wh", "description": "Webhooks", "quantity": 5000, "unit_price_cents": 2},
        ])
        assert inv.subtotal_cents == 110000
        assert inv.total_cents == 110000

    def test_discount(self):
        c = AppAPIDeveloperAPIApiUsageBillingCalculator()
        inv = c.create_invoice("inst-1", "inv-1", "2025-01", [
            {"item_id": "api", "description": "API", "quantity": 1000, "unit_price_cents": 100},
        ], discount_pct=10.0)
        assert inv.discount_cents == 10000
        assert inv.total_cents == 90000

    def test_total_revenue(self):
        c = AppAPIDeveloperAPIApiUsageBillingCalculator()
        c.create_invoice("inst-1", "inv-1", "2025-01", [{"item_id": "a", "description": "A", "quantity": 100, "unit_price_cents": 10}])
        c.create_invoice("inst-1", "inv-2", "2025-02", [{"item_id": "a", "description": "A", "quantity": 200, "unit_price_cents": 10}])
        assert c.total_revenue_cents("inst-1") == 3000

    def test_isolation(self):
        c = AppAPIDeveloperAPIApiUsageBillingCalculator()
        c.create_invoice("inst-1", "inv-1", "2025-01", [{"item_id": "a", "description": "A", "quantity": 100, "unit_price_cents": 10}])
        assert c.total_revenue_cents("inst-2") == 0
