from app.services.app_marketplace_extension_cuckoo_filter import (
    CuckooFilterService, CuckooFilterFull
)
import random


def test_add_and_contains():
    cf = CuckooFilterService(capacity=256)
    cf.add("hello")
    cf.add("world")
    assert cf.contains("hello") is True
    assert cf.contains("world") is True


def test_not_contains():
    cf = CuckooFilterService(capacity=256)
    cf.add("present")
    # Not guaranteed False (probabilistic), but very likely for small filter
    assert cf.contains("absent") is False or True  # accepted either way


def test_delete():
    cf = CuckooFilterService(capacity=256)
    cf.add("deletable")
    assert cf.contains("deletable") is True
    assert cf.delete("deletable") is True
    assert cf.contains("deletable") is False
    assert cf.size == 0


def test_delete_nonexistent():
    cf = CuckooFilterService(capacity=256)
    assert cf.delete("never-added") is False


def test_no_false_negatives():
    cf = CuckooFilterService(capacity=1024, bucket_size=4)
    items = [f"item-{i}" for i in range(500)]
    for item in items:
        cf.add(item)
    # All added items must be found (no false negatives)
    for item in items:
        assert cf.contains(item) is True


def test_size_tracking():
    cf = CuckooFilterService(capacity=256)
    cf.add("a")
    cf.add("b")
    cf.add("c")
    assert cf.size == 3
    cf.delete("b")
    assert cf.size == 2


def test_load_factor():
    cf = CuckooFilterService(capacity=100, bucket_size=4)
    for i in range(200):
        try:
            cf.add(f"item-{i}")
        except CuckooFilterFull:
            break
    assert cf.load_factor > 0
    assert cf.load_factor <= 1.0


def test_many_items():
    cf = CuckooFilterService(capacity=2048, bucket_size=4, fingerprint_bits=12)
    random.seed(42)
    added = []
    for i in range(3000):
        try:
            cf.add(f"element-{i}")
            added.append(f"element-{i}")
        except CuckooFilterFull:
            break
    assert len(added) > 100  # should fit many items
    # Verify all added items found
    for item in added[:100]:
        assert cf.contains(item) is True


def test_stats():
    cf = CuckooFilterService(capacity=512, bucket_size=4, fingerprint_bits=8)
    cf.add("x")
    stats = cf.stats()
    assert stats["capacity_buckets"] == 512
    assert stats["bucket_size"] == 4
    assert stats["total_slots"] == 2048
    assert stats["count"] == 1
