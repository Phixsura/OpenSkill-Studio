from app.services.app_marketplace_extension_retry_policy import (
    RetryPolicyEngineService, RetryPolicy, RetryStrategy
)


def test_exponential_backoff():
    svc = RetryPolicyEngineService()
    policy = RetryPolicy(strategy=RetryStrategy.EXPONENTIAL,
                         base_delay_ms=100, jitter=False)
    assert svc.calculate_delay(policy, 0) == 100   # 100 * 2^0
    assert svc.calculate_delay(policy, 1) == 200   # 100 * 2^1
    assert svc.calculate_delay(policy, 2) == 400   # 100 * 2^2


def test_linear_backoff():
    svc = RetryPolicyEngineService()
    policy = RetryPolicy(strategy=RetryStrategy.LINEAR,
                         base_delay_ms=100, jitter=False)
    assert svc.calculate_delay(policy, 0) == 100   # 100 * 1
    assert svc.calculate_delay(policy, 1) == 200   # 100 * 2
    assert svc.calculate_delay(policy, 2) == 300   # 100 * 3


def test_fixed_backoff():
    svc = RetryPolicyEngineService()
    policy = RetryPolicy(strategy=RetryStrategy.FIXED,
                         base_delay_ms=500, jitter=False)
    assert svc.calculate_delay(policy, 0) == 500
    assert svc.calculate_delay(policy, 5) == 500


def test_max_delay_cap():
    svc = RetryPolicyEngineService()
    policy = RetryPolicy(strategy=RetryStrategy.EXPONENTIAL,
                         base_delay_ms=1000, max_delay_ms=5000, jitter=False)
    # 2^10 * 1000 = 1024000 but capped at 5000
    assert svc.calculate_delay(policy, 10) == 5000


def test_jitter_adds_variance():
    svc = RetryPolicyEngineService()
    policy = RetryPolicy(strategy=RetryStrategy.FIXED,
                         base_delay_ms=1000, jitter=True, jitter_factor=0.5)
    delays = {svc.calculate_delay(policy, 0) for _ in range(20)}
    assert len(delays) > 1  # should have variation


def test_max_attempts_stops_retry():
    svc = RetryPolicyEngineService()
    svc.register("test-op", RetryPolicy(max_attempts=2))
    should, _, _ = svc.should_retry("test-op", "timeout", 500, attempt=0)
    assert should is True
    should, _, reason = svc.should_retry("test-op", "timeout", 500, attempt=2)
    assert should is False
    assert "Max attempts" in reason


def test_non_retryable_status():
    svc = RetryPolicyEngineService()
    should, _, reason = svc.should_retry("op", "error", 404, attempt=0)
    assert should is False
    assert "not retryable" in reason


def test_429_minimum_delay():
    svc = RetryPolicyEngineService()
    svc.register("api", RetryPolicy(base_delay_ms=100, jitter=False))
    should, delay, _ = svc.should_retry("api", "rate_limited", 429, attempt=0)
    assert should is True
    assert delay >= 5000


def test_budget():
    svc = RetryPolicyEngineService()
    svc.register("limited-op", budget=2)
    svc.should_retry("limited-op", "timeout", 500, attempt=0)
    svc.should_retry("limited-op", "timeout", 500, attempt=1)
    should, _, reason = svc.should_retry("limited-op", "timeout", 500, attempt=0)
    assert should is False
    assert "budget exhausted" in reason


def test_simulate():
    svc = RetryPolicyEngineService()
    svc.register("sim", RetryPolicy(max_attempts=3))
    result = svc.simulate("sim", [
        ("timeout", 503), ("timeout", 503),  # 2 failures then implicit success
    ])
    assert result.success is True
    assert len(result.attempts) == 2


def test_simulate_failure():
    svc = RetryPolicyEngineService()
    svc.register("sim-fail", RetryPolicy(max_attempts=2))
    result = svc.simulate("sim-fail", [
        ("timeout", 503), ("timeout", 503), ("timeout", 503),
    ])
    assert result.success is False
