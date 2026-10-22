"""Parametrized idempotency store tests."""

import pytest
from app.services.idempotency import make_key, store_response, get_cached_response

RESPONSES = [
    {"status": "ok"},
    {"data": [1, 2, 3]},
    {"error": "not_found"},
    {},
    {"nested": {"deep": True}},
]

@pytest.mark.parametrize("response", RESPONSES)
def test_store_retrieve(response):
    k = make_key(f"client-{id(response)}", "POST", "/test")
    store_response(k, response)
    assert get_cached_response(k) == response

@pytest.mark.parametrize("response", RESPONSES)
def test_store_with_status(response):
    k = make_key(f"status-{id(response)}", "POST", "/test")
    store_response(k, response, 201)
    assert get_cached_response(k) == response

def test_miss():
    assert get_cached_response("nonexistent-key-xyz") is None

def test_overwrite():
    k = make_key("ow", "POST", "/ow")
    store_response(k, {"v": 1})
    store_response(k, {"v": 2})
    assert get_cached_response(k) == {"v": 2}
