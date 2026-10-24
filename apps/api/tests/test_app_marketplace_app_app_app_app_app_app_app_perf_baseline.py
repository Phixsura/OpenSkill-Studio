from app.services.app_marketplace_app_app_app_app_app_app_app_perf_baseline import establish_baseline, compare_to_baseline

def test_baseline():
    r = establish_baseline("/api/users", [50, 60, 70, 80, 90, 100, 110, 120, 130, 200])
    assert r["established"]
    assert r["samples"] == 10
    assert r["p50"] == 100

def test_compare_stable():
    baseline = establish_baseline("/api", [50, 60, 70, 80, 90, 100] * 10)
    current = establish_baseline("/api", [55, 65, 75, 85, 95, 105] * 10)
    r = compare_to_baseline(baseline, current)
    assert r["verdict"] == "stable"

def test_compare_regression():
    baseline = establish_baseline("/api", [50] * 100)
    current = establish_baseline("/api", [200] * 100)
    r = compare_to_baseline(baseline, current)
    assert r["regression"]
