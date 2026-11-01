"""App cache tests."""
import pytest
from app.services.app_cache import cache_get, cache_set, cache_delete, cache_clear, cache_size

@pytest.fixture(autouse=True)
def _clean():
    cache_clear()
    yield
    cache_clear()

def test_set_get():
    cache_set("k1", "value1")
    assert cache_get("k1") == "value1"

def test_miss():
    assert cache_get("nonexistent") is None

def test_delete():
    cache_set("k1", "v1")
    assert cache_delete("k1") is True
    assert cache_get("k1") is None

def test_delete_missing():
    assert cache_delete("nope") is False

def test_clear():
    cache_set("a", 1)
    cache_set("b", 2)
    count = cache_clear()
    assert count == 2
    assert cache_size() == 0

def test_size():
    cache_set("a", 1)
    cache_set("b", 2)
    assert cache_size() == 2

def test_overwrite():
    cache_set("k", "old")
    cache_set("k", "new")
    assert cache_get("k") == "new"

def test_complex_value():
    cache_set("k", {"data": [1, 2, 3], "nested": {"deep": True}})
    assert cache_get("k")["nested"]["deep"] is True
