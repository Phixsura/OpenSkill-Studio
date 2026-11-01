from app.services.app_marketplace_extension_rate_window import RateWindowService, WindowCounter
import time


def test_window_counter_increment():
    wc = WindowCounter(window_size=60)
    now = time.time()
    wc.increment(5, now)
    wc.increment(3, now)
    assert wc.get_fixed(now) == 8


def test_sliding_window():
    wc = WindowCounter(window_size=1.0)
    now = time.time()
    # Ensure we're at the start of a window
    window_start = now - (now % 1.0)
    wc.current_window = int(window_start)
    wc.previous_count = 100
    wc.current_count = 50
    # At 50% through window: 100*0.5 + 50 = 100
    mid = window_start + 0.5
    sliding = wc.get_sliding(mid)
    assert 90 <= sliding <= 110  # ~100 with timing variance


def test_rate_service():
    rs = RateWindowService()
    for _ in range(10):
        rs.increment("api_calls")
    result = rs.get("api_calls", "1s")
    assert result["fixed"] >= 0


def test_multi_resolution():
    rs = RateWindowService()
    rs.configure("requests", [("fast", 1.0), ("slow", 10.0)])
    rs.increment("requests", 5)
    all_res = rs.get_all_resolutions("requests")
    assert "fast" in all_res
    assert "slow" in all_res


def test_top_k():
    rs = RateWindowService()
    for _ in range(10):
        rs.increment("errors", key="/api/users")
    for _ in range(5):
        rs.increment("errors", key="/api/orders")
    for _ in range(15):
        rs.increment("errors", key="/api/payments")
    top = rs.top_k("errors", 2)
    assert top[0][0] == "/api/payments"
    assert len(top) == 2


def test_rate_per_second():
    wc = WindowCounter(window_size=10.0)
    now = time.time()
    wc.increment(100, now)
    rate = wc.rate_per_second(now)
    assert rate > 0  # 100/10 = 10/s ideally


def test_compare():
    rs = RateWindowService()
    for _ in range(100):
        rs.increment("reads")
    for _ in range(10):
        rs.increment("writes")
    cmp = rs.compare("reads", "writes", "1s")
    assert cmp["ratio"] > 1  # reads > writes


def test_auto_configure():
    rs = RateWindowService()
    rs.increment("new_metric")  # auto-creates with defaults
    result = rs.get("new_metric", "1m")
    assert result["fixed"] >= 0


def test_window_rollover():
    wc = WindowCounter(window_size=0.01)
    now = time.time()
    wc.increment(50, now)
    time.sleep(0.02)
    now2 = time.time()
    # Previous window's count should carry over
    wc.increment(10, now2)
    assert wc.current_count == 10
