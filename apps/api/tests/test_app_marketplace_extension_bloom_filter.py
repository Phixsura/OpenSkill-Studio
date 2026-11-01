from app.services.app_marketplace_extension_bloom_filter import (
    BloomFilterService, BloomFilter, BloomFilterParams
)


def test_optimal_params():
    p = BloomFilterParams(expected_elements=1000, false_positive_rate=0.01)
    assert p.bit_size > 0
    assert p.hash_count > 0
    # For 1000 elements at 1% FPR, optimal is ~9585 bits, ~7 hashes
    assert 5000 < p.bit_size < 20000
    assert 3 <= p.hash_count <= 15


def test_add_and_contains():
    svc = BloomFilterService()
    bf = svc.create("test", 100, 0.01)
    bf.add("hello")
    bf.add("world")
    assert bf.contains("hello") is True
    assert bf.contains("world") is True


def test_no_false_negatives():
    svc = BloomFilterService()
    bf = svc.create("test", 1000, 0.01)
    items = [f"item-{i}" for i in range(500)]
    for item in items:
        bf.add(item)
    # Bloom filters NEVER have false negatives
    for item in items:
        assert bf.contains(item) is True


def test_definitely_not_in_set():
    svc = BloomFilterService()
    bf = svc.create("test", 100, 0.01)
    bf.add("exists")
    # Items never added should (usually) return False
    # With a good FPR, almost all should be False
    false_positives = sum(1 for i in range(1000)
                          if bf.contains(f"definitely-not-{i}"))
    # With 0.01 FPR and 1 element in a 100-capacity filter, FP rate is very low
    assert false_positives < 50  # very generous bound


def test_estimated_count():
    svc = BloomFilterService()
    bf = svc.create("test", 100, 0.01)
    for i in range(25):
        bf.add(f"item-{i}")
    assert bf.estimated_count == 25


def test_duplicate_add():
    svc = BloomFilterService()
    bf = svc.create("test", 100, 0.01)
    bf.add("same")
    bf.add("same")
    bf.add("same")
    assert bf.estimated_count == 1


def test_current_fpr():
    svc = BloomFilterService()
    bf = svc.create("test", 100, 0.01)
    assert bf.current_fpr == 0.0  # empty filter
    for i in range(50):
        bf.add(f"item-{i}")
    assert bf.current_fpr > 0  # non-zero after adding elements


def test_union():
    svc = BloomFilterService()
    bf1 = svc.create("a", 100, 0.01)
    bf2 = BloomFilter(bf1.params)
    bf1.add("alice")
    bf2.add("bob")
    combined = bf1.union(bf2)
    assert combined.contains("alice") is True
    assert combined.contains("bob") is True


def test_union_different_sizes_rejected():
    p1 = BloomFilterParams(100, 0.01)
    p2 = BloomFilterParams(200, 0.01)
    bf1 = BloomFilter(p1)
    bf2 = BloomFilter(p2)
    try:
        bf1.union(bf2)
        assert False
    except ValueError:
        pass


def test_stats():
    svc = BloomFilterService()
    bf = svc.create("test", 1000, 0.01)
    for i in range(100):
        bf.add(f"item-{i}")
    stats = bf.stats()
    assert stats["elements_added"] == 100
    assert stats["bits_set"] > 0
    assert 0 < stats["fill_ratio"] < 1
    assert stats["memory_bytes"] > 0


def test_memory_efficiency():
    # 10K elements at 1% FPR should use ~12KB (much less than storing all elements)
    p = BloomFilterParams(10000, 0.01)
    bf = BloomFilter(p)
    assert bf.stats()["memory_bytes"] < 15000  # <15KB
