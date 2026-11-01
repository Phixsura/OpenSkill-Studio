from app.services.app_marketplace_extension_api_throttle import (
    ApiThrottleService, ThrottleLevel, SystemMetrics,
)


def test_normal_conditions():
    svc = ApiThrottleService()
    state = svc.evaluate("ext-1", SystemMetrics(cpu_percent=40, error_rate_percent=1))
    assert state.level == ThrottleLevel.NONE
    assert state.throughput == 1.0


def test_light_throttle():
    svc = ApiThrottleService()
    state = svc.evaluate("ext-1", SystemMetrics(cpu_percent=75))
    assert state.level == ThrottleLevel.LIGHT
    assert state.throughput == 0.8


def test_moderate_throttle():
    svc = ApiThrottleService()
    state = svc.evaluate("ext-1", SystemMetrics(cpu_percent=90))
    assert state.level == ThrottleLevel.MODERATE
    assert state.throughput == 0.5


def test_heavy_throttle():
    svc = ApiThrottleService()
    state = svc.evaluate("ext-1", SystemMetrics(cpu_percent=96))
    assert state.level == ThrottleLevel.HEAVY
    assert state.throughput == 0.2


def test_error_rate_throttle():
    svc = ApiThrottleService()
    state = svc.evaluate("ext-1", SystemMetrics(error_rate_percent=35))
    assert state.level == ThrottleLevel.HEAVY


def test_manual_override():
    svc = ApiThrottleService()
    svc.set_override("ext-1", ThrottleLevel.BLOCK)
    state = svc.evaluate("ext-1", SystemMetrics(cpu_percent=10))
    assert state.level == ThrottleLevel.BLOCK
    assert state.reason == "manual override"


def test_clear_override():
    svc = ApiThrottleService()
    svc.set_override("ext-1", ThrottleLevel.BLOCK)
    svc.clear_override("ext-1")
    state = svc.evaluate("ext-1", SystemMetrics(cpu_percent=10))
    assert state.level == ThrottleLevel.NONE


def test_block_denies_all():
    svc = ApiThrottleService()
    svc.set_override("ext-1", ThrottleLevel.BLOCK)
    svc.evaluate("ext-1", SystemMetrics())
    assert svc.should_allow("ext-1") is False
    info = svc.get_state("ext-1")
    assert info["throttled"] == 1


def test_none_allows_all():
    svc = ApiThrottleService()
    assert svc.should_allow("ext-1") is True
    info = svc.get_state("ext-1")
    assert info["allowed"] == 1
