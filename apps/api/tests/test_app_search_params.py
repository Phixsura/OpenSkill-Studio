"""App search — function signature and parameter validation."""

import inspect
import pytest
from app.services.app_search import search_marketplace_apps

def test_default_sort():
    assert inspect.signature(search_marketplace_apps).parameters["sort_by"].default == "relevance"

def test_default_page():
    assert inspect.signature(search_marketplace_apps).parameters["page"].default == 1

def test_default_per_page():
    assert inspect.signature(search_marketplace_apps).parameters["per_page"].default == 20

def test_query_optional():
    p = inspect.signature(search_marketplace_apps).parameters["query"]
    assert p.default is None or p.default == inspect.Parameter.empty

def test_category_optional():
    p = inspect.signature(search_marketplace_apps).parameters["category"]
    assert p.default is None

def test_return_type_hint():
    hints = inspect.get_annotations(search_marketplace_apps)
    assert "return" in hints
