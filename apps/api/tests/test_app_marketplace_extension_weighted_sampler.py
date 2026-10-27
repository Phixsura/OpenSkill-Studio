from app.services.app_marketplace_extension_weighted_sampler import WeightedSamplerService


def test_sample_one():
    ws = WeightedSamplerService(seed=42)
    items = ["a", "b", "c"]
    weights = [10, 1, 1]
    # "a" should be chosen most often
    counts = {"a": 0, "b": 0, "c": 0}
    for _ in range(100):
        counts[ws.sample_one(items, weights)] += 1
    assert counts["a"] > 60  # ~83% expected


def test_sample_n_with_replacement():
    ws = WeightedSamplerService(seed=42)
    result = ws.sample_n(["x", "y"], [1, 1], n=10, replacement=True)
    assert len(result) == 10


def test_sample_n_without_replacement():
    ws = WeightedSamplerService(seed=42)
    result = ws.sample_n(["a", "b", "c", "d"], [1, 1, 1, 1],
                          n=3, replacement=False)
    assert len(result) == 3
    assert len(set(result)) == 3  # all unique


def test_no_replacement_too_many():
    ws = WeightedSamplerService()
    try:
        ws.sample_n(["a", "b"], [1, 1], n=5, replacement=False)
        assert False
    except ValueError:
        pass


def test_weighted_shuffle():
    ws = WeightedSamplerService(seed=42)
    items = ["heavy", "medium", "light"]
    weights = [100, 10, 1]
    # Heavy should usually be first
    first_counts = {"heavy": 0, "medium": 0, "light": 0}
    for _ in range(100):
        shuffled = ws.weighted_shuffle(items, weights)
        first_counts[shuffled[0]] += 1
    assert first_counts["heavy"] > 70


def test_alias_table():
    ws = WeightedSamplerService(seed=42)
    weights = [0.5, 0.3, 0.2]
    prob, alias = ws.build_alias_table(weights)
    assert len(prob) == 3
    assert len(alias) == 3
    # Sample and verify distribution
    counts = [0, 0, 0]
    for _ in range(10000):
        idx = ws.alias_sample(prob, alias)
        counts[idx] += 1
    # Should roughly match weights
    assert counts[0] > counts[1] > counts[2]


def test_distribution():
    ws = WeightedSamplerService(seed=42)
    dist = ws.distribution_test(["a", "b"], [75, 25], num_samples=10000)
    assert 65 < dist["a"] < 85  # ~75%
    assert 15 < dist["b"] < 35  # ~25%


def test_single_item():
    ws = WeightedSamplerService()
    assert ws.sample_one(["only"], [1]) == "only"


def test_zero_weight():
    ws = WeightedSamplerService(seed=42)
    # Zero-weight items should never be selected
    counts = {"a": 0, "b": 0}
    for _ in range(100):
        counts[ws.sample_one(["a", "b"], [1, 0])] += 1
    assert counts["b"] == 0
