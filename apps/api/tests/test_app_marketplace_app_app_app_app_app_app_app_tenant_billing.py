from app.services.app_marketplace_app_app_app_app_app_app_app_tenant_billing import calculate_bill, usage_summary

def test_bill():
    r = calculate_bill([
        {"resource": "compute_hours", "quantity": 100},
        {"resource": "storage_gb", "quantity": 50},
        {"resource": "compute_hours", "quantity": 50},
    ], rates={"compute_hours": 0.10, "storage_gb": 0.05})
    assert r["total"] == 17.5  # 150*0.10 + 50*0.05
    assert len(r["line_items"]) == 2

def test_summary():
    r = usage_summary([
        {"tenant_id": "t1", "total": 500},
        {"tenant_id": "t2", "total": 1000},
        {"tenant_id": "t3", "total": 200},
    ])
    assert r["total_cost"] == 1700
    assert r["top_spenders"][0]["tenant"] == "t2"
