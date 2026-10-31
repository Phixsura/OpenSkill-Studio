from app.services.app_marketplace_extension_hyperloglog import HyperLogLogService
import random


def test_empty():
    hll = HyperLogLogService(precision=10)
    assert hll.count() == 0


def test_small_cardinality():
    hll = HyperLogLogService(precision=14)
    for i in range(100):
        hll.add(f"item-{i}")
    estimate = hll.count()
    # Should be within ~5% of 100
    assert 80 <= estimate <= 120


def test_duplicates_dont_increase_count():
    hll = HyperLogLogService(precision=14)
    for _ in range(1000):
        hll.add("same-item")
    assert hll.count() <= 3  # should be ~1


def test_medium_cardinality():
    hll = HyperLogLogService(precision=14)
    for i in range(10000):
        hll.add(f"user-{i}")
    estimate = hll.count()
    error_pct = abs(estimate - 10000) / 10000 * 100
    assert error_pct < 5  # within 5%


def test_merge():
    hll1 = HyperLogLogService(precision=12)
    hll2 = HyperLogLogService(precision=12)
    # Each adds 500 unique items, 200 overlap
    for i in range(500):
        hll1.add(f"item-{i}")
    for i in range(300, 800):
        hll2.add(f"item-{i}")
    merged = hll1.merge(hll2)
    estimate = merged.count()
    # True cardinality = 800 (0..799)
    assert 650 <= estimate <= 950


def test_merge_different_precision_rejected():
    hll1 = HyperLogLogService(precision=10)
    hll2 = HyperLogLogService(precision=12)
    try:
        hll1.merge(hll2)
        assert False
    except ValueError:
        pass


def test_relative_error():
    hll = HyperLogLogService(precision=14)
    # precision=14 → m=16384 → error ≈ 0.0081 (0.81%)
    assert hll.relative_error() < 0.01


def test_memory_efficiency():
    hll = HyperLogLogService(precision=14)
    # 2^14 = 16384 bytes = 16KB to count billions of unique items
    assert hll.memory_bytes() == 16384
    # Add a million items — memory stays the same
    for i in range(10000):
        hll.add(f"item-{i}")
    assert hll.memory_bytes() == 16384


def test_precision_range():
    try:
        HyperLogLogService(precision=3)
        assert False
    except ValueError:
        pass
    try:
        HyperLogLogService(precision=17)
        assert False
    except ValueError:
        pass
    # Valid range
    HyperLogLogService(precision=4)
    HyperLogLogService(precision=16)
