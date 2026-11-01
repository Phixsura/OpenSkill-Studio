from app.services.app_marketplace_extension_sampling import SamplingStrategyService


def test_fixed_rate():
    ss = SamplingStrategyService()
    sampled = sum(1 for i in range(1000)
                  if ss.fixed_rate(f"evt-{i}", {}, rate=10).sampled)
    # ~10% should be sampled
    assert 70 < sampled < 130


def test_fixed_rate_deterministic():
    ss = SamplingStrategyService()
    r1 = ss.fixed_rate("event-42", {}, rate=5)
    r2 = ss.fixed_rate("event-42", {}, rate=5)
    assert r1.sampled == r2.sampled  # same event → same decision


def test_probabilistic():
    ss = SamplingStrategyService()
    sampled = sum(1 for i in range(10000)
                  if ss.probabilistic(f"evt-{i}", {}, 0.05).sampled)
    assert 300 < sampled < 700  # ~5% of 10000


def test_priority_critical_always_kept():
    ss = SamplingStrategyService(seed=42)
    for _ in range(100):
        result = ss.priority_sample("evt", {}, "critical", base_rate=0.01)
        assert result.sampled is True


def test_priority_normal_sampled():
    ss = SamplingStrategyService(seed=42)
    sampled = sum(1 for i in range(1000)
                  if ss.priority_sample(f"evt-{i}", {}, "normal", 0.1).sampled)
    assert 50 < sampled < 200


def test_reservoir_fixed_size():
    ss = SamplingStrategyService(seed=42)
    ss.reset_reservoir(size=50)
    for i in range(10000):
        ss.reservoir_sample({"value": i})
    reservoir = ss.get_reservoir()
    assert len(reservoir) == 50


def test_reservoir_uniform():
    ss = SamplingStrategyService(seed=42)
    ss.reset_reservoir(size=100)
    for i in range(10000):
        ss.reservoir_sample({"value": i})
    reservoir = ss.get_reservoir()
    # Should be roughly uniform across the stream
    values = [r["value"] for r in reservoir]
    avg = sum(values) / len(values)
    assert 3000 < avg < 7000  # ~5000 if truly uniform


def test_adaptive_rate():
    ss = SamplingStrategyService()
    rate = ss.adaptive_rate(target_per_second=100, current_volume=1000)
    assert rate == 0.1
    rate2 = ss.adaptive_rate(target_per_second=100, current_volume=50)
    assert rate2 == 1.0  # volume below target → keep all


def test_weighted_estimate():
    ss = SamplingStrategyService()
    # Sampled 100 events at 10% rate → estimate ~1000 true events
    estimate = ss.weighted_estimate(100, 0.1)
    assert estimate == 1000.0


def test_sample_rate_in_result():
    ss = SamplingStrategyService()
    result = ss.fixed_rate("evt-1", {}, rate=20)
    assert result.sample_rate == 0.05  # 1/20
