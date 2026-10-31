from app.services.app_marketplace_app_app_app_app_app_app_app_latency_pctl import compute_percentiles, check_slo, bucket_latencies

def test_percentiles():
    lats = list(range(1, 101))  # 1 to 100
    r = compute_percentiles(lats)
    assert r["count"] == 100
    assert r["p50"] == 51
    assert r["p99"] == 100
    assert r["min"] == 1
    assert r["max"] == 100

def test_slo():
    p = {"p50": 50, "p99": 200}
    r = check_slo(p, {"p50": 100, "p99": 150})
    assert not r["met"]
    assert len(r["violations"]) == 1
    assert r["violations"][0]["metric"] == "p99"

def test_buckets():
    lats = [5, 15, 50, 150, 500]
    r = bucket_latencies(lats, [10, 50, 100, 500])
    assert r["buckets"]["<=10ms"] == 1
    assert r["buckets"]["<=50ms"] == 2
