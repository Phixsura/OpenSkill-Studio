"""Parametrized permission summary tests."""

import pytest
from app.services.app_permissions import get_permission_summary

CASES = [
    ([], 0, 0, 0, 0),
    (["read:cohorts"], 1, 1, 0, 0),
    (["write:projects"], 1, 0, 1, 0),
    (["subscribe:events"], 1, 0, 0, 1),
    (["read:cohorts", "write:projects"], 2, 1, 1, 0),
    (["read:cohorts", "read:projects", "write:projects", "subscribe:events", "extend:ui"], 5, 2, 1, 2),
]

@pytest.mark.parametrize("perms,total,reads,writes,special", CASES)
def test_summary(perms, total, reads, writes, special):
    s = get_permission_summary(perms)
    assert s["total"] == total
    assert s["read_count"] == reads
    assert s["write_count"] == writes
    assert s["special_count"] == special
