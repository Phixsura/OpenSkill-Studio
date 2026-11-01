from app.services.app_marketplace_app_circuit_breaker import create_circuit_breaker, record_result, should_allow_request

def test_create():
    cb = create_circuit_breaker(name="api-gateway", failure_threshold=3)
    assert cb["state"] == "closed"
    assert cb["failure_threshold"] == 3

def test_trip():
    cb = create_circuit_breaker(name="test", failure_threshold=2)
    cb = record_result(breaker=cb, success=False)
    assert cb["state"] == "closed"
    cb = record_result(breaker=cb, success=False)
    assert cb["state"] == "open"

def test_closed_allows():
    cb = create_circuit_breaker(name="test")
    r = should_allow_request(breaker=cb)
    assert r["allowed"]

def test_open_blocks():
    cb = create_circuit_breaker(name="test")
    cb["state"] = "open"
    cb["last_failure_at"] = datetime.utcnow().isoformat()
    r = should_allow_request(breaker=cb)
    assert not r["allowed"]

from datetime import datetime
