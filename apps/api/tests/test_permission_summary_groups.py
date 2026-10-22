"""Permission summary grouping tests."""

import pytest
from app.services.app_permissions import get_permission_summary

def test_groups_by_action():
    perms = ["read:cohorts", "read:projects", "write:cohorts", "subscribe:events", "extend:ui"]
    summary = get_permission_summary(perms)
    assert isinstance(summary, dict)

def test_all_permissions_counted():
    perms = ["read:cohorts", "write:projects", "subscribe:events"]
    summary = get_permission_summary(perms)
    total = summary.get("total", 0)
    assert total == 3

def test_empty_permissions():
    summary = get_permission_summary([])
    assert isinstance(summary, dict)

def test_single_permission():
    summary = get_permission_summary(["read:cohorts"])
    assert isinstance(summary, dict)
    assert len(summary) >= 1

LARGE_PERM_SET = [
    "read:cohorts", "write:cohorts", "read:projects", "write:projects",
    "read:submissions", "read:skills", "write:skills", "read:analytics",
    "subscribe:events", "extend:ui", "run:background_jobs",
    "read:talent", "write:talent", "export:analytics",
]

def test_large_perm_set():
    summary = get_permission_summary(LARGE_PERM_SET)
    assert isinstance(summary, dict)
    assert len(summary) >= 2  # At least read + write groups
