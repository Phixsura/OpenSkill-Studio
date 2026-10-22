"""Marketplace stats tests."""
import pytest
from app.services.app_marketplace_stats import compute_marketplace_stats

def test_empty():
    s = compute_marketplace_stats()
    assert s["total_apps"] == 0
    assert s["avg_installs_per_app"] == 0

def test_with_data():
    s = compute_marketplace_stats(total_apps=50, published_apps=30, total_developers=10,
        total_installations=300, apps_by_category={"connector": 15, "automation": 10, "analytics": 5})
    assert s["published_apps"] == 30
    assert s["avg_installs_per_app"] == 10.0
    assert s["top_categories"][0][0] == "connector"

def test_top_categories_limited():
    cats = {f"cat_{i}": i for i in range(10)}
    s = compute_marketplace_stats(apps_by_category=cats)
    assert len(s["top_categories"]) == 5

def test_all_keys():
    s = compute_marketplace_stats(total_apps=1, published_apps=1, total_installations=5)
    expected = {"total_apps", "published_apps", "total_developers", "total_installations",
                "apps_by_category", "top_categories", "avg_installs_per_app"}
    assert set(s.keys()) == expected
