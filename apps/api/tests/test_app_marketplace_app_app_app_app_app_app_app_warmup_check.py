from app.services.app_marketplace_app_app_app_app_app_app_app_warmup_check import run_warmup, estimate_warmup_time

def test_warmup():
    r = run_warmup([
        {"name": "api", "health": "ok", "latency_ms": 50, "threshold_ms": 500},
        {"name": "db", "health": "ok", "latency_ms": 10, "threshold_ms": 100},
        {"name": "cache", "health": "error", "latency_ms": 5000, "threshold_ms": 100},
    ])
    assert r["ready"] == 2
    assert not r["all_ready"]

def test_estimate():
    r = estimate_warmup_time([{"warmup_sec": 10}, {"warmup_sec": 30}, {"warmup_sec": 5}])
    assert r["estimated_parallel_sec"] == 30
    assert r["total_sequential_sec"] == 45
