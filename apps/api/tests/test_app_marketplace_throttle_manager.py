from app.services.app_marketplace_throttle_manager import (
    ThrottleManager, ThrottleConfig,
)


def test_allow_within_limit():
    tm = ThrottleManager()
    tm.configure("api", ThrottleConfig(requests_per_window=10, window_seconds=60, burst_limit=5))
    for _ in range(10):
        ok, info = tm.allow("api")
        assert ok is True
    ok, info = tm.allow("api")
    assert ok is False
    assert info["reason"] == "rate_limit"


def test_burst_limit():
    tm = ThrottleManager()
    tm.configure("burst", ThrottleConfig(requests_per_window=1000, burst_limit=3))
    for _ in range(3):
        ok, _ = tm.allow("burst")
        assert ok is True
    ok, info = tm.allow("burst")
    assert ok is False
    assert info["reason"] == "burst_limit"


def test_adaptive_under_load():
    tm = ThrottleManager(server_load=0.0)
    tm.configure("adaptive", ThrottleConfig(requests_per_window=100, adaptive=True, load_threshold=0.5))
    stats_normal = tm.get_stats("adaptive")
    assert stats_normal["effective_limit"] == 100

    tm.set_server_load(0.9)
    stats_loaded = tm.get_stats("adaptive")
    assert stats_loaded["effective_limit"] < 100  # reduced under load


def test_remaining_info():
    tm = ThrottleManager()
    tm.configure("info", ThrottleConfig(requests_per_window=50, burst_limit=50))
    ok, info = tm.allow("info")
    assert ok is True
    assert info["remaining"] == 48  # 50 - 1 - 1 (the one just used)


def test_reset():
    tm = ThrottleManager()
    tm.configure("reset", ThrottleConfig(requests_per_window=5, burst_limit=5))
    for _ in range(5):
        tm.allow("reset")
    assert tm.allow("reset")[0] is False
    tm.reset("reset")
    assert tm.allow("reset")[0] is True


def test_default_config():
    tm = ThrottleManager()
    ok, _ = tm.allow("unconfigured")
    assert ok is True  # uses default ThrottleConfig
