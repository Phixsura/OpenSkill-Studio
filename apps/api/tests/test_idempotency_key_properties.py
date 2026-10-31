"""Idempotency key mathematical properties."""

import pytest
from app.services.idempotency import make_key

def test_deterministic():
    k1 = make_key("c", "POST", "/api/v1/test")
    k2 = make_key("c", "POST", "/api/v1/test")
    assert k1 == k2

def test_no_collisions():
    """100 distinct inputs produce 100 distinct keys."""
    keys = {make_key(f"client-{i}", "POST", f"/path-{i}") for i in range(100)}
    assert len(keys) == 100

def test_method_matters():
    assert make_key("c", "GET", "/p") != make_key("c", "POST", "/p")

def test_path_matters():
    assert make_key("c", "POST", "/a") != make_key("c", "POST", "/b")

def test_client_matters():
    assert make_key("a", "POST", "/p") != make_key("b", "POST", "/p")

def test_key_is_string():
    assert isinstance(make_key("c", "POST", "/p"), str)

def test_key_nonempty():
    assert len(make_key("c", "POST", "/p")) > 0

def test_key_no_whitespace():
    k = make_key("c", "POST", "/p")
    assert k.strip() == k
