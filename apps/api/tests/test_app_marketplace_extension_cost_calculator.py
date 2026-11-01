from app.services.app_marketplace_extension_cost_calculator import ExtCostCalculatorService

def test_estimate():
    svc = ExtCostCalculatorService()
    est = svc.estimate({"api_calls": 50, "storage": 10})
    assert est.subtotal_cents == 750  # 50*10 + 10*25
    assert est.total_cents == 750

def test_discount():
    svc = ExtCostCalculatorService()
    est = svc.estimate({"api_calls": 100}, discount_pct=20)
    assert est.subtotal_cents == 1000
    assert est.discount_cents == 200
    assert est.total_cents == 800

def test_compare_plans():
    svc = ExtCostCalculatorService()
    results = svc.compare_plans({"api_calls": 50, "storage": 5})
    assert len(results) == 3
    assert results[0]["plan"] == "Free"
    # Enterprise should be cheapest for high usage due to included + discount
    assert results[2]["total_cents"] <= results[0]["total_cents"]
