from datetime import UTC, datetime, timedelta
from app.services.app_timeout_handler import check_timeout, format_timeout_error

def test_not_timed_out():
    started = datetime.now(UTC).isoformat()
    r = check_timeout(started, timeout_seconds=60)
    assert r["timed_out"] is False
    assert r["remaining_seconds"] > 0

def test_timed_out():
    started = (datetime.now(UTC) - timedelta(seconds=120)).isoformat()
    r = check_timeout(started, timeout_seconds=60)
    assert r["timed_out"] is True

def test_elapsed():
    started = (datetime.now(UTC) - timedelta(seconds=30)).isoformat()
    r = check_timeout(started, timeout_seconds=60)
    assert 29 <= r["elapsed_seconds"] <= 31

def test_format_error():
    e = format_timeout_error(function_name="process", timeout_seconds=30, elapsed_seconds=35.2)
    assert e["error_type"] == "TimeoutError"
    assert "process" in e["message"]
    assert "30s" in e["message"]
