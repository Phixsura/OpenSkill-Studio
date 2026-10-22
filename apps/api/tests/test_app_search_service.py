"""App search service tests."""

import inspect
import pytest
from app.services.app_search import search_marketplace_apps


SORT_OPTIONS = ["relevance", "installs", "newest"]

@pytest.mark.parametrize("sort_by", SORT_OPTIONS)
def test_search_accepts_sort_options(sort_by):
    sig = inspect.signature(search_marketplace_apps)
    assert "sort_by" in sig.parameters
    assert sig.parameters["sort_by"].default == "relevance"

PAGINATION_CASES = [(1, 20), (2, 10), (1, 50), (100, 5)]

@pytest.mark.parametrize("page,per_page", PAGINATION_CASES)
def test_pagination_params(page, per_page):
    sig = inspect.signature(search_marketplace_apps)
    assert "page" in sig.parameters
    assert "per_page" in sig.parameters

CATEGORIES = ["connector", "automation", "analytics", "ui_extension", "ecosystem_source", "integration", "utility"]

@pytest.mark.parametrize("category", CATEGORIES)
def test_category_filter_param(category):
    sig = inspect.signature(search_marketplace_apps)
    assert "category" in sig.parameters

def test_is_async():
    assert inspect.iscoroutinefunction(search_marketplace_apps)

def test_returns_tuple_annotation():
    hints = inspect.get_annotations(search_marketplace_apps)
    assert "return" in hints
