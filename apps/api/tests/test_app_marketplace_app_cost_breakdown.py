from app.services.app_marketplace_app_cost_breakdown import calculate_cost_breakdown

def test_breakdown():
    resources = [
        {"name": "API Calls", "category": "compute", "quantity": 100000, "unit": "calls", "unit_price": 0.0001},
        {"name": "Storage", "category": "storage", "quantity": 50, "unit": "GB", "unit_price": 0.023},
        {"name": "Bandwidth", "category": "network", "quantity": 100, "unit": "GB", "unit_price": 0.09},
    ]
    r = calculate_cost_breakdown(resources=resources)
    assert r["total"] == 20.15  # 10 + 1.15 + 9.0
    assert r["largest_category"] == "compute"
    assert r["item_count"] == 3

def test_empty():
    r = calculate_cost_breakdown(resources=[])
    assert r["total"] == 0
    assert r["largest_category"] is None
