"""Tests for App Cost Tracker — recording, totals, categories."""

import pytest

from app.services.app_cost_tracker import AppCostTracker


class TestRecordCost:
    def test_record(self):
        t = AppCostTracker()
        e = t.record_cost("inst-1", "c1", "compute", 1500, "EC2 usage")
        assert e.amount_cents == 1500
        assert e.category == "compute"

    def test_negative_amount(self):
        t = AppCostTracker()
        with pytest.raises(ValueError, match="non-negative"):
            t.record_cost("inst-1", "c1", "compute", -100)

    def test_missing_category(self):
        t = AppCostTracker()
        with pytest.raises(ValueError, match="category"):
            t.record_cost("inst-1", "c1", "", 100)


class TestTotals:
    def test_total_cents(self):
        t = AppCostTracker()
        t.record_cost("inst-1", "c1", "compute", 1000)
        t.record_cost("inst-1", "c2", "storage", 500)
        assert t.total_cents("inst-1") == 1500

    def test_total_dollars(self):
        t = AppCostTracker()
        t.record_cost("inst-1", "c1", "compute", 2500)
        assert t.total_dollars("inst-1") == 25.0

    def test_total_since(self):
        t = AppCostTracker()
        t.record_cost("inst-1", "c1", "compute", 1000, now=1000.0)
        t.record_cost("inst-1", "c2", "compute", 2000, now=2000.0)
        assert t.total_cents("inst-1", since=1500.0) == 2000

    def test_empty(self):
        t = AppCostTracker()
        assert t.total_cents("inst-1") == 0


class TestByCategory:
    def test_breakdown(self):
        t = AppCostTracker()
        t.record_cost("inst-1", "c1", "compute", 1000)
        t.record_cost("inst-1", "c2", "compute", 500)
        t.record_cost("inst-1", "c3", "storage", 300)
        cats = t.by_category("inst-1")
        assert cats["compute"] == 1500
        assert cats["storage"] == 300


class TestGetEntries:
    def test_newest_first(self):
        t = AppCostTracker()
        t.record_cost("inst-1", "c1", "compute", 100, now=1000.0)
        t.record_cost("inst-1", "c2", "storage", 200, now=1001.0)
        entries = t.get_entries("inst-1")
        assert entries[0].entry_id == "c2"

    def test_filter_category(self):
        t = AppCostTracker()
        t.record_cost("inst-1", "c1", "compute", 100)
        t.record_cost("inst-1", "c2", "storage", 200)
        entries = t.get_entries("inst-1", category="compute")
        assert len(entries) == 1


class TestIsolation:
    def test_cross_installation(self):
        t = AppCostTracker()
        t.record_cost("inst-1", "c1", "compute", 1000)
        assert t.total_cents("inst-2") == 0
