from datetime import UTC, datetime, timedelta
from app.services.app_oauth_token_introspection import introspect_token

def test_active():
    future = (datetime.now(UTC) + timedelta(hours=1)).isoformat()
    r = introspect_token({"expires_at": future, "scope": "read:cohorts", "client_id": "c1"})
    assert r["active"] is True
    assert r["scope"] == "read:cohorts"

def test_expired():
    past = (datetime.now(UTC) - timedelta(hours=1)).isoformat()
    r = introspect_token({"expires_at": past})
    assert r["active"] is False

def test_empty():
    assert introspect_token({})["active"] is False  # empty dict is falsy

def test_none():
    assert introspect_token(None)["active"] is False

def test_unix_timestamp():
    future_ts = datetime.now(UTC).timestamp() + 3600
    r = introspect_token({"exp": future_ts, "client_id": "x"})
    assert r["active"] is True
