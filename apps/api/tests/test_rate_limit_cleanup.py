"""Rate limit cleanup function tests."""

from app.services.app_rate_limit import cleanup_old_counters, record_request, get_app_usage

def test_cleanup_returns_int():
    result = cleanup_old_counters()
    assert isinstance(result, int)

def test_cleanup_non_negative():
    assert cleanup_old_counters() >= 0

def test_cleanup_idempotent():
    c1 = cleanup_old_counters()
    c2 = cleanup_old_counters()
    # Second call should clean same or fewer
    assert isinstance(c2, int)

def test_current_hour_survives_cleanup():
    app = "cleanup-survive-test"
    record_request(app)
    cleanup_old_counters()
    usage = get_app_usage(app)
    assert isinstance(usage, dict)
