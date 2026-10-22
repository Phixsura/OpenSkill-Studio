"""Event replay service tests."""

import pytest
from app.services.app_event_replay import create_replay_request, validate_replay_request, _is_safe_replay_url

def test_create_replay():
    r = create_replay_request(event_id="e1", event_type="submission.completed",
        original_data={"id": "sub-1"}, target_url="https://x.com/hook", installation_id="i1")
    assert r["original_event_id"] == "e1"
    assert r["status"] == "pending"
    assert r["replay_id"].startswith("replay_")

def test_validate_no_event_type():
    r = validate_replay_request(event_type="", target_url="https://x.com")
    assert r["allowed"] is False

def test_validate_no_url():
    r = validate_replay_request(event_type="test", target_url="")
    assert r["allowed"] is False

def test_validate_bad_url():
    r = validate_replay_request(event_type="test", target_url="ftp://x.com")
    assert r["allowed"] is False

def test_validate_rate_limit():
    r = validate_replay_request(event_type="test", target_url="https://x.com",
        max_replays_per_hour=5, current_replays_this_hour=5)
    assert r["allowed"] is False

# SSRF protection
def test_ssrf_localhost():
    errors = _is_safe_replay_url("http://127.0.0.1/hook")
    assert len(errors) > 0

def test_ssrf_private():
    errors = _is_safe_replay_url("http://10.0.0.1/hook")
    assert len(errors) > 0

def test_ssrf_empty():
    errors = _is_safe_replay_url("")
    assert len(errors) > 0

def test_ssrf_bad_scheme():
    errors = _is_safe_replay_url("ftp://evil.com")
    assert len(errors) > 0
