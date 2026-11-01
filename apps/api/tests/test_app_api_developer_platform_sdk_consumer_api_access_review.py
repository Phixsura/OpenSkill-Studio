"""Tests for Consumer API Access Review service."""
import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_access_review import (
    AccessReviewManager, AccessEntry,
)


class TestAccessReviewManager:
    def _entries(self):
        return [
            AccessEntry("e1", "c1", "/api/users", "read"),
            AccessEntry("e2", "c1", "/api/admin", "write"),
            AccessEntry("e3", "c2", "/api/billing", "read"),
        ]

    def test_create_review(self):
        svc = AccessReviewManager()
        result = svc.create_review("r1", "2024-Q4", self._entries())
        assert result["entries"] == 3

    def test_decide(self):
        svc = AccessReviewManager()
        svc.create_review("r1", "Q4", self._entries())
        result = svc.decide("r1", "e1", "approved", "admin")
        assert result["decision"] == "approved"

    def test_complete(self):
        svc = AccessReviewManager()
        svc.create_review("r1", "Q4", self._entries())
        svc.decide("r1", "e1", "approved", "admin")
        svc.decide("r1", "e2", "revoked", "admin", "No longer needed")
        svc.decide("r1", "e3", "approved", "admin")
        result = svc.complete("r1")
        assert result["completed"] is True
        assert result["revoked"] == 1

    def test_incomplete(self):
        svc = AccessReviewManager()
        svc.create_review("r1", "Q4", self._entries())
        svc.decide("r1", "e1", "approved", "admin")
        result = svc.complete("r1")
        assert result["completed"] is False
        assert result["undecided"] == 2

    def test_progress(self):
        svc = AccessReviewManager()
        svc.create_review("r1", "Q4", self._entries())
        svc.decide("r1", "e1", "approved", "admin")
        progress = svc.get_progress("r1")
        assert progress["decided"] == 1
        assert progress["remaining"] == 2

    def test_get_decisions(self):
        svc = AccessReviewManager()
        svc.create_review("r1", "Q4", self._entries())
        svc.decide("r1", "e1", "approved", "admin")
        decisions = svc.get_decisions("r1")
        assert len(decisions) == 3
        assert decisions[0]["decision"] == "approved"
        assert decisions[1]["decision"] == "pending"

    def test_invalid_decision(self):
        svc = AccessReviewManager()
        svc.create_review("r1", "Q4", self._entries())
        with pytest.raises(ValueError):
            svc.decide("r1", "e1", "maybe", "admin")

    def test_completed_review_locked(self):
        svc = AccessReviewManager()
        entries = [AccessEntry("e1", "c1", "/api", "read")]
        svc.create_review("r1", "Q4", entries)
        svc.decide("r1", "e1", "approved", "admin")
        svc.complete("r1")
        with pytest.raises(ValueError):
            svc.decide("r1", "e1", "revoked", "admin")

    def test_stats(self):
        svc = AccessReviewManager()
        svc.create_review("r1", "Q4", self._entries())
        for e in self._entries():
            svc.decide("r1", e.entry_id, "approved", "admin")
        svc.complete("r1")
        stats = svc.get_stats()
        assert stats["completed"] == 1
        assert stats["total_entries_reviewed"] == 3

    def test_empty_entries(self):
        svc = AccessReviewManager()
        with pytest.raises(ValueError):
            svc.create_review("r1", "Q4", [])

    def test_isolation(self):
        a, b = AccessReviewManager(), AccessReviewManager()
        a.create_review("r1", "Q4", self._entries())
        assert b.list_reviews() == []
