"""Parametrized idempotency key tests."""

import pytest
from app.services.idempotency import make_key, store_response, get_cached_response

METHODS = ["GET", "POST", "PATCH", "PUT", "DELETE"]
PATHS = ["/api/v1/test", "/api/v1/apps", "/api/v1/orgs/123/install"]
CLIENTS = ["client-a", "client-b", "client-c"]

@pytest.mark.parametrize("method", METHODS)
def test_key_per_method(method):
    k = make_key("c1", method, "/path")
    assert isinstance(k, str)
    assert len(k) == 64  # SHA-256 hex

@pytest.mark.parametrize("path", PATHS)
def test_key_per_path(path):
    k = make_key("c1", "POST", path)
    assert len(k) == 64

@pytest.mark.parametrize("client", CLIENTS)
def test_key_per_client(client):
    k = make_key(client, "POST", "/test")
    assert len(k) == 64

def test_store_and_retrieve():
    k = make_key("idem-param", "POST", "/unique-path")
    store_response(k, {"ok": True})
    assert get_cached_response(k) == {"ok": True}

def test_different_methods_different_keys():
    keys = {make_key("c", m, "/p") for m in METHODS}
    assert len(keys) == 5

def test_different_paths_different_keys():
    keys = {make_key("c", "POST", p) for p in PATHS}
    assert len(keys) == 3

def test_different_clients_different_keys():
    keys = {make_key(c, "POST", "/p") for c in CLIENTS}
    assert len(keys) == 3
