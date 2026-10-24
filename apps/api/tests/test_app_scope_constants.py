"""Scope constants tests."""
from app.services.app_scope_constants import ALL_SCOPES, ALL_READ, ALL_WRITE, ALL_SPECIAL

def test_all_scopes_count():
    assert len(ALL_SCOPES) >= 15

def test_no_duplicates():
    assert len(ALL_SCOPES) == len(set(ALL_SCOPES))

def test_read_format():
    for s in ALL_READ:
        assert s.startswith("read:")

def test_write_format():
    for s in ALL_WRITE:
        assert s.startswith("write:")

def test_all_combined():
    assert len(ALL_SCOPES) == len(ALL_READ) + len(ALL_WRITE) + len(ALL_SPECIAL)
