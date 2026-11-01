from app.services.app_marketplace_app_app_app_app_app_app_app_lat_percentile import calculate_percentiles, compare_percentiles

def test_percentiles():
    r = calculate_percentiles([10, 20, 30, 40, 50, 60, 70, 80, 90, 100])
    assert r["samples"] == 10
    assert r["p50"] == 60
    assert r["min"] == 10
    assert r["max"] == 100

def test_compare():
    b = calculate_percentiles([50] * 100)
    c = calculate_percentiles([80] * 100)
    r = compare_percentiles(b, c)
    assert r["regression"]
    assert r["changes"]["p99"]["delta"] == 30
