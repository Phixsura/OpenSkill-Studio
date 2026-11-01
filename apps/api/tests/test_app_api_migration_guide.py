"""Tests for App API Migration Guide — create, steps, completion."""

import pytest

from app.services.app_api_migration_guide import AppAPIMigrationGuide

STEPS = [
    {"step_id": "s1", "title": "Update auth", "description": "Switch to OAuth2", "breaking": True},
    {"step_id": "s2", "title": "Update endpoints", "description": "Use /v2 paths"},
]


class TestCreate:
    def test_create(self):
        m = AppAPIMigrationGuide()
        g = m.create_guide("inst-1", "g1", "v1", "v2", STEPS)
        assert len(g.steps) == 2
        assert g.breaking_count == 1

    def test_no_steps(self):
        m = AppAPIMigrationGuide()
        with pytest.raises(ValueError):
            m.create_guide("inst-1", "g1", "v1", "v2", [])


class TestCompletion:
    def test_mark(self):
        m = AppAPIMigrationGuide()
        m.create_guide("inst-1", "g1", "v1", "v2", STEPS)
        m.mark_completed("inst-1", "g1", "consumer-a")
        m.mark_completed("inst-1", "g1", "consumer-b")
        assert m.completion_count("inst-1", "g1") == 2

    def test_dedup(self):
        m = AppAPIMigrationGuide()
        m.create_guide("inst-1", "g1", "v1", "v2", STEPS)
        m.mark_completed("inst-1", "g1", "consumer-a")
        m.mark_completed("inst-1", "g1", "consumer-a")
        assert m.completion_count("inst-1", "g1") == 1


class TestIsolation:
    def test_cross(self):
        m = AppAPIMigrationGuide()
        m.create_guide("inst-1", "g1", "v1", "v2", STEPS)
        assert m.list_guides("inst-2") == []
