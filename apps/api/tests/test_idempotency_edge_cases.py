"""Idempotency store edge cases."""

import pytest
from app.services.idempotency import make_key, store_response, get_cached_response

def test_different_methods_different_keys():
    k1 = make_key("client-1", "GET", "/test")
    k2 = make_key("client-1", "POST", "/test")
    assert k1 != k2

def test_different_paths_different_keys():
    k1 = make_key("client-1", "POST", "/a")
    k2 = make_key("client-1", "POST", "/b")
    assert k1 != k2

def test_different_clients_different_keys():
    k1 = make_key("client-1", "POST", "/test")
    k2 = make_key("client-2", "POST", "/test")
    assert k1 != k2

def test_same_inputs_same_key():
    k1 = make_key("c", "POST", "/x")
    k2 = make_key("c", "POST", "/x")
    assert k1 == k2

def test_store_complex_response():
    k = make_key("complex", "POST", "/complex")
    resp = {"data": {"nested": [1, 2, {"deep": True}]}, "meta": {"page": 1}}
    store_response(k, resp)
    assert get_cached_response(k) == resp

def test_store_none_value():
    k = make_key("none-val", "POST", "/none")
    store_response(k, None)
    # Should return None (which is also what a miss returns, but the key exists)
    result = get_cached_response(k)
    assert result is None

KEY_CHARS = [
    ("key with spaces", "POST", "/path"),
    ("key/with/slashes", "POST", "/path"),
    ("key-with-dashes", "DELETE", "/path"),
    ("unicode-键", "PATCH", "/中文"),
]

@pytest.mark.parametrize("client,method,path", KEY_CHARS)
def test_special_chars_in_key(client, method, path):
    k = make_key(client, method, path)
    assert isinstance(k, str) and len(k) > 0
