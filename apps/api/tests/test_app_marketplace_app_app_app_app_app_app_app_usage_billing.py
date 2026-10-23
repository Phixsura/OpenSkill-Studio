from app.services.app_marketplace_app_app_app_app_app_app_app_usage_billing import calculate_bill

def test_billing():
    r = calculate_bill(api_calls=150000, storage_gb=50, base_price=29)
    assert r["api_cost"] > 0  # beyond free tier
    assert r["storage_cost"] == 5.0
    assert r["total"] > 34  # base + api + storage
    assert len(r["breakdown"]) >= 2  # free tier + paid tier

def test_free_tier():
    r = calculate_bill(api_calls=5000)
    assert r["api_cost"] == 0
    assert r["total"] == 0
