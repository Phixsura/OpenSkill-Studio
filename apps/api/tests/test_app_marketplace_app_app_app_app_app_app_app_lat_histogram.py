from app.services.app_marketplace_app_app_app_app_app_app_app_lat_histogram import build_histogram, compare_histograms

def test_histogram():
    r = build_histogram([5, 10, 20, 50, 100, 200, 500, 1000, 2000, 5000])
    assert r["total"] == 10
    assert r["counts"]["le_5"] == 1
    assert r["counts"]["le_100"] == 5
    assert r["counts"]["le_inf"] == 10

def test_compare():
    b = build_histogram([10, 20, 30, 40, 50])
    c = build_histogram([100, 200, 300, 400, 500])
    r = compare_histograms(b, c)
    assert r["regression"]
