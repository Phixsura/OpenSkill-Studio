from app.services.app_marketplace_app_pricing_calculator import calculate_platform_fee

def test_small():
    r = calculate_platform_fee(gross_revenue=5000)
    assert r["total_fee"] == 1500.0  # 30% of 5000
    assert r["net_revenue"] == 3500.0

def test_tiered():
    r = calculate_platform_fee(gross_revenue=50000)
    # 10K @ 30% = 3000, 40K @ 20% = 8000 => 11000
    assert r["total_fee"] == 11000.0
    assert r["effective_rate"] == 22.0

def test_negative():
    r = calculate_platform_fee(gross_revenue=-100)
    assert "error" in r

def test_zero():
    r = calculate_platform_fee(gross_revenue=0)
    assert r["total_fee"] == 0
    assert r["net_revenue"] == 0
