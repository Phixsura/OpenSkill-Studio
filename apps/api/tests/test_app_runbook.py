"""Tests for App Runbook — create, search, execution."""

import pytest

from app.services.app_runbook import AppRunbook

STEPS = [
    {"instruction": "Check CPU usage", "expected_outcome": "< 80%"},
    {"instruction": "Restart service", "expected_outcome": "Service responds 200"},
]


class TestCreate:
    def test_create(self):
        r = AppRunbook()
        rb = r.create_runbook("inst-1", "rb1", "CPU Alert", "Handle high CPU", STEPS, tags=["infra"])
        assert len(rb.steps) == 2
        assert rb.tags == ["infra"]

    def test_empty_steps(self):
        r = AppRunbook()
        with pytest.raises(ValueError):
            r.create_runbook("inst-1", "rb1", "T", "D", [])


class TestExecution:
    def test_record(self):
        r = AppRunbook()
        r.create_runbook("inst-1", "rb1", "T", "D", STEPS)
        rb = r.record_execution("inst-1", "rb1")
        assert rb.execution_count == 1


class TestSearch:
    def test_by_query(self):
        r = AppRunbook()
        r.create_runbook("inst-1", "rb1", "CPU Alert", "High CPU", STEPS)
        r.create_runbook("inst-1", "rb2", "Disk Full", "Disk space", STEPS)
        results = r.search("inst-1", query="CPU")
        assert len(results) == 1

    def test_by_tag(self):
        r = AppRunbook()
        r.create_runbook("inst-1", "rb1", "A", "D", STEPS, tags=["infra"])
        r.create_runbook("inst-1", "rb2", "B", "D", STEPS, tags=["db"])
        results = r.search("inst-1", tag="infra")
        assert len(results) == 1


class TestIsolation:
    def test_cross_installation(self):
        r = AppRunbook()
        r.create_runbook("inst-1", "rb1", "T", "D", STEPS)
        with pytest.raises(KeyError):
            r.get_runbook("inst-2", "rb1")
