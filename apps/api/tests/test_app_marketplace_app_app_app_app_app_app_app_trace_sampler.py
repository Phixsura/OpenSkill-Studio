from app.services.app_marketplace_app_app_app_app_app_app_app_trace_sampler import AdaptiveSampler

def test_sampling():
    s = AdaptiveSampler(base_rate=0.5)
    results = [s.should_sample(f"trace-{i}")["sample"] for i in range(1000)]
    assert 350 < sum(results) < 650  # ~50%

def test_adapt():
    s = AdaptiveSampler()
    r = s.adapt(current_rps=1000, target_samples_per_sec=10)
    assert r["new_rate"] == 0.01  # 10/1000
    r2 = s.adapt(current_rps=5, target_samples_per_sec=10)
    assert r2["new_rate"] == 1.0  # capped at max
