from app.services.app_marketplace_app_app_app_app_app_app_app_span_sampler import SpanSampler

def test_always():
    s = SpanSampler(strategy="always")
    assert s.should_sample("t1")["sample"]
    assert s.should_sample("t2")["sample"]

def test_never():
    s = SpanSampler(strategy="never")
    assert not s.should_sample("t1")["sample"]

def test_probabilistic():
    s = SpanSampler(rate=0.5)
    results = [s.should_sample(f"trace-{i}")["sample"] for i in range(1000)]
    # Should be roughly 50%, allow wide margin
    assert 300 < sum(results) < 700
    stats = s.stats()
    assert stats["total"] == 1000
