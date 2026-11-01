from app.services.app_marketplace_api_rate_tracker import APIRateTracker


def test_record_and_get():
    art = APIRateTracker()
    art.record("ext-1", "GET", "/api/users", 45.0)
    art.record("ext-1", "GET", "/api/users", 55.0)
    stats = art.get_endpoint_stats("ext-1", "GET", "/api/users")
    assert stats is not None
    assert stats.total_calls == 2
    assert stats.avg_latency_ms == 50.0
    assert stats.min_latency_ms == 45.0
    assert stats.max_latency_ms == 55.0


def test_error_tracking():
    art = APIRateTracker()
    art.record("ext-2", "POST", "/api/data", 100.0, 200)
    art.record("ext-2", "POST", "/api/data", 50.0, 500)
    stats = art.get_endpoint_stats("ext-2", "POST", "/api/data")
    assert stats.total_errors == 1
    assert stats.error_rate == 50.0


def test_all_endpoints():
    art = APIRateTracker()
    for _ in range(10):
        art.record("ext-3", "GET", "/popular", 20.0)
    for _ in range(3):
        art.record("ext-3", "GET", "/rare", 30.0)
    endpoints = art.get_all_endpoints("ext-3")
    assert endpoints[0].path == "/popular"  # most calls first


def test_slowest():
    art = APIRateTracker()
    art.record("ext-4", "GET", "/fast", 10.0)
    art.record("ext-4", "GET", "/slow", 500.0)
    art.record("ext-4", "GET", "/medium", 100.0)
    slowest = art.get_slowest("ext-4", 2)
    assert slowest[0].path == "/slow"


def test_most_errors():
    art = APIRateTracker()
    art.record("ext-5", "GET", "/stable", 10.0, 200)
    art.record("ext-5", "GET", "/buggy", 10.0, 500)
    errors = art.get_most_errors("ext-5")
    assert errors[0].path == "/buggy"


def test_summary():
    art = APIRateTracker()
    art.record("ext-6", "GET", "/a", 50.0, 200)
    art.record("ext-6", "POST", "/b", 100.0, 201)
    art.record("ext-6", "GET", "/a", 60.0, 500)
    summary = art.get_summary("ext-6")
    assert summary["endpoints"] == 2
    assert summary["total_calls"] == 3
    assert summary["total_errors"] == 1
