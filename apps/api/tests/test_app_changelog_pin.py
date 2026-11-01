"""Tests for App Changelog Pin — pin, unpin, limits."""

import pytest

from app.services.app_changelog_pin import AppChangelogPin


class TestPin:
    def test_pin(self):
        p = AppChangelogPin()
        e = p.pin("inst-1", "e1", "2.0.0", "Breaking API change", reason="Important")
        assert e.entry_id == "e1"
        assert p.pin_count("inst-1") == 1

    def test_duplicate(self):
        p = AppChangelogPin()
        p.pin("inst-1", "e1", "1.0", "Title")
        with pytest.raises(ValueError, match="already pinned"):
            p.pin("inst-1", "e1", "1.0", "Title")

    def test_max_pins(self):
        p = AppChangelogPin(max_pins=2)
        p.pin("inst-1", "e1", "1.0", "A")
        p.pin("inst-1", "e2", "1.0", "B")
        with pytest.raises(ValueError, match="Maximum"):
            p.pin("inst-1", "e3", "1.0", "C")


class TestUnpin:
    def test_unpin(self):
        p = AppChangelogPin()
        p.pin("inst-1", "e1", "1.0", "Title")
        assert p.unpin("inst-1", "e1") is True
        assert p.pin_count("inst-1") == 0

    def test_unpin_nonexistent(self):
        p = AppChangelogPin()
        assert p.unpin("inst-1", "nope") is False


class TestQuery:
    def test_is_pinned(self):
        p = AppChangelogPin()
        p.pin("inst-1", "e1", "1.0", "Title")
        assert p.is_pinned("inst-1", "e1") is True
        assert p.is_pinned("inst-1", "e2") is False

    def test_list(self):
        p = AppChangelogPin()
        p.pin("inst-1", "e1", "1.0", "A")
        p.pin("inst-1", "e2", "2.0", "B")
        assert len(p.list_pins("inst-1")) == 2


class TestIsolation:
    def test_cross_installation(self):
        p = AppChangelogPin()
        p.pin("inst-1", "e1", "1.0", "Title")
        assert p.is_pinned("inst-2", "e1") is False
