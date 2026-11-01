from app.services.app_marketplace_extension_count_min_sketch import CountMinSketchService


def test_basic_count():
    cms = CountMinSketchService(width=1000, depth=5)
    cms.add("apple", 3)
    cms.add("banana", 7)
    assert cms.estimate("apple") >= 3
    assert cms.estimate("banana") >= 7


def test_never_underestimates():
    cms = CountMinSketchService(width=500, depth=5)
    counts = {"a": 100, "b": 50, "c": 200, "d": 10}
    for item, count in counts.items():
        cms.add(item, count)
    for item, true_count in counts.items():
        assert cms.estimate(item) >= true_count


def test_unseen_item():
    cms = CountMinSketchService(width=1000, depth=5)
    cms.add("seen")
    est = cms.estimate("never-seen")
    assert est >= 0  # might have false positive, never negative


def test_accuracy():
    cms = CountMinSketchService(epsilon=0.001, delta=0.01)
    # Add items with known frequencies
    for i in range(1000):
        cms.add(f"item-{i % 10}")  # 10 items, each 100 times
    for i in range(10):
        est = cms.estimate(f"item-{i}")
        assert 95 <= est <= 105  # should be ~100, allow small error


def test_merge():
    cms1 = CountMinSketchService(width=500, depth=5)
    cms2 = CountMinSketchService(width=500, depth=5)
    cms1.add("x", 10)
    cms2.add("x", 20)
    cms2.add("y", 5)
    merged = cms1.merge(cms2)
    assert merged.estimate("x") >= 30
    assert merged.estimate("y") >= 5
    assert merged.total_count == 35


def test_merge_different_sizes_rejected():
    cms1 = CountMinSketchService(width=100, depth=3)
    cms2 = CountMinSketchService(width=200, depth=3)
    try:
        cms1.merge(cms2)
        assert False
    except ValueError:
        pass


def test_heavy_hitters():
    cms = CountMinSketchService(width=1000, depth=5)
    cms.add("popular", 500)
    cms.add("normal", 50)
    cms.add("rare", 5)
    # Total = 555, 1% threshold = 5.55
    hitters = cms.heavy_hitters(1.0, ["popular", "normal", "rare"])
    names = [h[0] for h in hitters]
    assert "popular" in names
    assert "normal" in names


def test_total_count():
    cms = CountMinSketchService(width=100, depth=3)
    cms.add("a", 10)
    cms.add("b", 20)
    assert cms.total_count == 30


def test_optimal_params():
    # epsilon=0.01, delta=0.01 → w=ceil(e/0.01)=272, d=ceil(ln(1/0.01))=5
    cms = CountMinSketchService(epsilon=0.01, delta=0.01)
    stats = cms.stats()
    assert stats["width"] >= 200
    assert stats["depth"] >= 4
