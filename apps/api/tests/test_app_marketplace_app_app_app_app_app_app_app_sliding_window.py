from app.services.app_marketplace_app_app_app_app_app_app_app_sliding_window import (
    record_request, check_rate, window_stats, clear_windows,
)

def test_rate():
    clear_windows()
    now = 1000.0
    for i in range(5):
        record_request("user1", now + i * 0.1)
    r = check_rate("user1", window_sec=60, limit=10, now=now + 1)
    assert r["allowed"]
    assert r["count"] == 5
    assert r["remaining"] == 5
    clear_windows()

def test_exceeded():
    clear_windows()
    now = 1000.0
    for i in range(10):
        record_request("u2", now)
    r = check_rate("u2", window_sec=60, limit=10, now=now)
    assert not r["allowed"]
    assert r["remaining"] == 0
    clear_windows()
