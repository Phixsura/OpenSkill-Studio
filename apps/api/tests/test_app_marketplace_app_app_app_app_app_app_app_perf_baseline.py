from app.services.app_marketplace_app_app_app_app_app_app_app_perf_baseline import establish_baseline, compare_to_baseline

def test_baseline():
    r = establish_baseline([50, 60, 70, 80, 90, 100, 110, 120, 130, 140])
    assert r["established"]
    assert r["avg"] == 95.0
    assert r["p50"] == 100

def test_compare():
    baseline = establish_baseline([50, 60, 70, 80, 90])
    current = establish_baseline([80, 90, 100, 110, 120])
    r = compare_to_baseline(baseline, current)
    assert r["has_regression"]
