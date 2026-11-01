"""Tests for App API Release Note — create, publish, list."""

import pytest
from app.services.app_api_release_note import AppAPIReleaseNote


class TestCreate:
    def test_create(self):
        r = AppAPIReleaseNote()
        n = r.create("inst-1", "n1", "v2.0", "Major Release", ["Dark mode", "New API"])
        assert len(n.highlights) == 2
        assert n.published is False

    def test_duplicate(self):
        r = AppAPIReleaseNote()
        r.create("inst-1", "n1", "v1", "A")
        with pytest.raises(ValueError):
            r.create("inst-1", "n1", "v2", "B")


class TestPublish:
    def test_publish(self):
        r = AppAPIReleaseNote()
        r.create("inst-1", "n1", "v2.0", "Release")
        r.publish("inst-1", "n1")
        assert len(r.published_notes("inst-1")) == 1


class TestIsolation:
    def test_cross(self):
        r = AppAPIReleaseNote()
        r.create("inst-1", "n1", "v1", "A")
        assert r.list_notes("inst-2") == []
