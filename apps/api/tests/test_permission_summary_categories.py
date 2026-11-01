"""Permission summary category grouping."""

import pytest
from app.services.app_permissions import get_permission_summary

def test_read_category():
    s = get_permission_summary(["read:cohorts", "read:projects"])
    assert "read" in s.get("categories", {})

def test_write_category():
    s = get_permission_summary(["write:cohorts"])
    assert "write" in s.get("categories", {})

def test_subscribe_category():
    s = get_permission_summary(["subscribe:events"])
    cats = s.get("categories", {})
    assert "subscribe" in cats

def test_read_count():
    s = get_permission_summary(["read:cohorts", "read:projects", "read:skills"])
    assert s.get("read_count", 0) == 3

def test_write_count():
    s = get_permission_summary(["write:cohorts", "write:projects"])
    assert s.get("write_count", 0) == 2

def test_special_count():
    s = get_permission_summary(["subscribe:events", "extend:ui", "run:background_jobs"])
    assert s.get("special_count", 0) == 3
