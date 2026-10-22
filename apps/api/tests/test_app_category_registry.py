"""App category registry tests."""
import pytest
from app.services.app_category_registry import get_category, list_categories, get_category_keys, CATEGORIES

@pytest.mark.parametrize("key", CATEGORIES.keys())
def test_get_category(key):
    c = get_category(key)
    assert c is not None
    assert c.key == key
    assert len(c.label) > 0
    assert len(c.icon) > 0

def test_get_unknown():
    assert get_category("unknown") is None

def test_list_categories():
    cats = list_categories()
    assert len(cats) == 7

def test_get_keys():
    keys = get_category_keys()
    assert "connector" in keys
    assert keys == sorted(keys)  # alphabetical
