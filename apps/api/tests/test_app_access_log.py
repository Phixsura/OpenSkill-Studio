"""App access log tests."""
import pytest
from app.services.app_access_log import log_access, get_access_log, get_access_stats

def test_log_and_get():
    log_access(key_id="k1", method="GET", path="/api/v1/test", status=200)
    entries = get_access_log("k1")
    assert len(entries) >= 1

def test_stats():
    key = "stats-key"
    log_access(key_id=key, method="GET", path="/ok", status=200)
    log_access(key_id=key, method="POST", path="/fail", status=400)
    s = get_access_stats(key)
    assert s["total_requests"] >= 2
    assert s["success"] >= 1
    assert s["errors"] >= 1

def test_empty():
    assert get_access_log("nonexistent") == []
    assert get_access_stats("nonexistent")["total_requests"] == 0

def test_limit():
    key = "limit-key"
    for i in range(100):
        log_access(key_id=key, method="GET", path=f"/p{i}", status=200)
    assert len(get_access_log(key, limit=5)) == 5
