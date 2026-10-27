from app.services.app_marketplace_extension_debounce_throttle import DebounceThrottleService
import time


def test_debounce_schedules():
    dt = DebounceThrottleService()
    result = dt.debounce_call("search", 100, query="hello")
    assert result["status"] == "scheduled"


def test_debounce_resets_timer():
    dt = DebounceThrottleService()
    dt.debounce_call("search", 50, query="h")
    dt.debounce_call("search", 50, query="he")
    dt.debounce_call("search", 50, query="hel")
    # Only last args kept
    dc = dt._debounced["search"]
    assert dc.last_kwargs == {"query": "hel"}
    assert dc.suppressed_count == 3


def test_debounce_fires_after_delay():
    dt = DebounceThrottleService()
    dt.debounce_call("key", 10)  # 10ms
    time.sleep(0.02)
    result = dt.check_debounce("key")
    assert result is not None
    assert result["fired_count"] == 1


def test_debounce_not_ready():
    dt = DebounceThrottleService()
    dt.debounce_call("key", 1000)  # 1 second
    result = dt.check_debounce("key")
    assert result is None


def test_flush_debounce():
    dt = DebounceThrottleService()
    dt.debounce_call("key", 10000, "important")
    result = dt.flush_debounce("key")
    assert result is not None
    assert result["flushed"] is True
    assert "important" in result["args"]


def test_cancel_debounce():
    dt = DebounceThrottleService()
    dt.debounce_call("key", 10000)
    assert dt.cancel_debounce("key") is True
    assert dt.check_debounce("key") is None


def test_throttle_first_allowed():
    dt = DebounceThrottleService()
    result = dt.throttle_call("api", 100, endpoint="/users")
    assert result["status"] == "fired"


def test_throttle_suppresses():
    dt = DebounceThrottleService()
    dt.throttle_call("api", 1000)  # 1 second window
    result = dt.throttle_call("api", 1000)  # too soon
    assert result["status"] == "suppressed"
    assert result["next_allowed_in_ms"] > 0


def test_throttle_allows_after_interval():
    dt = DebounceThrottleService()
    dt.throttle_call("api", 10)  # 10ms
    time.sleep(0.02)
    result = dt.throttle_call("api", 10)
    assert result["status"] == "fired"
    assert result["fired_count"] == 2


def test_stats():
    dt = DebounceThrottleService()
    dt.debounce_call("d", 100)
    dt.throttle_call("t", 100)
    dt.throttle_call("t", 100)  # suppressed
    stats_d = dt.get_stats("d")
    stats_t = dt.get_stats("t")
    assert stats_d["debounce"]["pending"] is True
    assert stats_t["throttle"]["suppressed"] == 1
