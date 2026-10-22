"""App listing formatter tests."""
import pytest
from app.services.app_listing_formatter import format_listing, format_listings

APP = {"id": "a1", "name": "Test", "slug": "test", "description": "Desc", "icon_url": None,
       "category": "connector", "developer_id": "d1"}
DEV = {"display_name": "Dev Studio", "verified": True}

def test_basic():
    r = format_listing(APP)
    assert r["name"] == "Test"
    assert r["developer_name"] is None

def test_with_developer():
    r = format_listing(APP, developer=DEV)
    assert r["developer_name"] == "Dev Studio"
    assert r["developer_verified"] is True

def test_with_stats():
    r = format_listing(APP, stats={"active_installs": 42, "health_score": 95})
    assert r["install_count"] == 42
    assert r["health_score"] == 95

def test_format_listings():
    result = format_listings([APP], developers={"d1": DEV})
    assert len(result) == 1
    assert result[0]["developer_name"] == "Dev Studio"

def test_format_empty():
    assert format_listings([]) == []
