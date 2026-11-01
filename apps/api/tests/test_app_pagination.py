"""Pagination helper tests."""
import pytest
from app.services.app_pagination import paginate

def test_first_page():
    p = paginate(total=100, page=1, per_page=20)
    assert p["page"] == 1
    assert p["total_pages"] == 5
    assert p["has_next"] is True
    assert p["has_prev"] is False
    assert p["offset"] == 0

def test_last_page():
    p = paginate(total=100, page=5, per_page=20)
    assert p["has_next"] is False
    assert p["has_prev"] is True

def test_single_page():
    p = paginate(total=5, page=1, per_page=20)
    assert p["total_pages"] == 1
    assert p["has_next"] is False

def test_clamp_page():
    p = paginate(total=10, page=999, per_page=10)
    assert p["page"] == 1

def test_clamp_per_page():
    p = paginate(total=10, page=1, per_page=500)
    assert p["per_page"] == 100

def test_zero_total():
    p = paginate(total=0, page=1, per_page=20)
    assert p["total_pages"] == 1
