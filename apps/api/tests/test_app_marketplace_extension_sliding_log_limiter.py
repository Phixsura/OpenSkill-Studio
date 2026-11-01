from app.services.app_marketplace_extension_sliding_log_limiter import SlidingLogLimiterService
import time


def test_basic_allow():
    svc = SlidingLogLimiterService()
    svc.configure_windows([("per_second", 1.0, 5)])
    result = svc.check("client-1")
    assert result["allowed"] is True
    assert result["remaining"]["per_second"] == 4.0


def test_rate_exceeded():
    svc = SlidingLogLimiterService()
    svc.configure_windows([("per_second", 1.0, 3)])
    for _ in range(3):
        svc.check("client-1")
    result = svc.check("client-1")
    assert result["allowed"] is False
    assert len(result["violations"]) == 1
    assert result["violations"][0]["window"] == "per_second"


def test_multi_window():
    svc = SlidingLogLimiterService()
    svc.configure_windows([("fast", 0.1, 2), ("slow", 10.0, 100)])
    svc.check("c1")
    svc.check("c1")
    result = svc.check("c1")
    assert result["allowed"] is False
    # Violated fast window but not slow
    assert any(v["window"] == "fast" for v in result["violations"])


def test_weighted_requests():
    svc = SlidingLogLimiterService()
    svc.configure_windows([("window", 10.0, 10)])
    # Heavy request costs 5
    svc.check("c1", weight=5)
    svc.check("c1", weight=5)
    result = svc.check("c1", weight=1)
    assert result["allowed"] is False


def test_burst_allowance():
    svc = SlidingLogLimiterService()
    svc.configure_windows([("window", 10.0, 3)])
    svc.set_burst("c1", 2)  # 3 + 2 = 5 effective limit
    for _ in range(5):
        r = svc.check("c1")
        assert r["allowed"] is True
    result = svc.check("c1")
    assert result["allowed"] is False


def test_window_slides():
    svc = SlidingLogLimiterService()
    svc.configure_windows([("window", 0.05, 2)])
    svc.check("c1")
    svc.check("c1")
    # At limit
    assert svc.check("c1")["allowed"] is False
    # Wait for window to slide
    time.sleep(0.06)
    result = svc.check("c1")
    assert result["allowed"] is True


def test_retry_after():
    svc = SlidingLogLimiterService()
    svc.configure_windows([("window", 1.0, 2)])
    svc.check("c1")
    svc.check("c1")
    result = svc.check("c1")
    assert result["violations"][0]["retry_after"] > 0


def test_usage_stats():
    svc = SlidingLogLimiterService()
    svc.configure_windows([("minute", 60.0, 100)])
    for _ in range(10):
        svc.check("c1")
    usage = svc.get_usage("c1")
    assert usage["minute"]["used"] == 10
    assert usage["minute"]["pct"] == 10.0


def test_independent_keys():
    svc = SlidingLogLimiterService()
    svc.configure_windows([("window", 10.0, 2)])
    svc.check("c1")
    svc.check("c1")
    # c1 at limit, c2 should be fine
    assert svc.check("c2")["allowed"] is True
    assert svc.check("c1")["allowed"] is False
