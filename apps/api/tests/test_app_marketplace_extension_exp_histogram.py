from app.services.app_marketplace_extension_exp_histogram import ExponentialHistogramService


def test_observe():
    h = ExponentialHistogramService(base=2, num_buckets=16, min_value=1)
    h.observe(5)
    h.observe(10)
    h.observe(20)
    assert h._count == 3
    assert h._min == 5
    assert h._max == 20


def test_quantiles():
    h = ExponentialHistogramService(base=2, num_buckets=32, min_value=1)
    for v in range(1, 101):
        h.observe(float(v))
    # p50 should be ~50
    assert 30 < h.p50 < 70
    # p99 should be ~99
    assert h.p99 > 80


def test_mean():
    h = ExponentialHistogramService()
    h.observe_many([10.0, 20.0, 30.0])
    assert h.mean == 20.0


def test_merge():
    h1 = ExponentialHistogramService(base=2, num_buckets=16, min_value=1)
    h2 = ExponentialHistogramService(base=2, num_buckets=16, min_value=1)
    h1.observe_many([1, 2, 3, 4, 5])
    h2.observe_many([6, 7, 8, 9, 10])
    merged = h1.merge(h2)
    assert merged._count == 10
    assert merged._min == 1
    assert merged._max == 10


def test_underflow():
    h = ExponentialHistogramService(base=2, num_buckets=16, min_value=10)
    h.observe(5)  # below min_value
    assert h._underflow == 1


def test_get_buckets():
    h = ExponentialHistogramService(base=2, num_buckets=8, min_value=1)
    h.observe(1.5)
    h.observe(3.0)
    h.observe(7.0)
    buckets = h.get_buckets()
    assert len(buckets) > 0
    assert all("count" in b and "lower" in b for b in buckets)


def test_stats():
    h = ExponentialHistogramService(base=2, num_buckets=16, min_value=1)
    for v in [10, 20, 30, 40, 50]:
        h.observe(float(v))
    stats = h.stats()
    assert stats["count"] == 5
    assert stats["mean"] == 30.0
    assert stats["min"] == 10
    assert stats["max"] == 50


def test_empty():
    h = ExponentialHistogramService()
    assert h.p50 == 0
    assert h.mean == 0
    assert h.stats()["count"] == 0


def test_single_value():
    h = ExponentialHistogramService(base=2, num_buckets=16, min_value=1)
    h.observe(42.0)
    assert h._count == 1
    assert h.mean == 42.0
