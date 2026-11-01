from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_trace_sampler import fleet_trace_sampler
def test_sampler():
    r = fleet_trace_sampler([{"spans_per_sec": 10000, "sampled_per_sec": 100}, {"spans_per_sec": 5000, "sampled_per_sec": 50}])
    assert r["total_spans_per_sec"] == 15000
    assert r["sample_rate_pct"] == 1.0
    assert r["adequate"]
