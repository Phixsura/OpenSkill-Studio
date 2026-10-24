from app.services.app_marketplace_app_app_app_app_app_app_app_ep_benchmark import run_benchmark, compare_benchmarks

def test_benchmark():
    latencies = [10, 15, 20, 25, 30, 50, 80, 100, 150, 200]
    r = run_benchmark(latencies, 10)
    assert r["samples"] == 10
    assert r["min_ms"] == 10
    assert r["max_ms"] == 200
    assert r["throughput_rps"] > 0

def test_compare():
    baseline = run_benchmark([50, 60, 70, 80, 90, 100] * 10, 60)
    current = run_benchmark([50, 60, 70, 80, 90, 100] * 10, 60)
    r = compare_benchmarks(baseline, current)
    assert not r["regression"]
    assert r["verdict"] == "ok"
