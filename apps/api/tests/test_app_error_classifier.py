"""Tests for App Error Classifier — classify, group, categories."""

import pytest

from app.services.app_error_classifier import AppErrorClassifier


class TestClassify:
    def test_classify(self):
        c = AppErrorClassifier()
        g = c.classify("inst-1", "TimeoutError", "Connection timed out", now=1000.0)
        assert g.category == "network"
        assert g.count == 1

    def test_groups_similar(self):
        c = AppErrorClassifier()
        c.classify("inst-1", "TimeoutError", "Connection timed out", now=1000.0)
        g = c.classify("inst-1", "TimeoutError", "Connection timed out", now=1001.0)
        assert g.count == 2
        assert g.last_seen == 1001.0

    def test_missing_error_type(self):
        c = AppErrorClassifier()
        with pytest.raises(ValueError, match="error_type"):
            c.classify("inst-1", "", "message")


class TestCategories:
    def test_auth(self):
        c = AppErrorClassifier()
        g = c.classify("inst-1", "AuthenticationError", "Invalid token")
        assert g.category == "auth"

    def test_validation(self):
        c = AppErrorClassifier()
        g = c.classify("inst-1", "ValidationError", "Invalid email")
        assert g.category == "validation"

    def test_not_found(self):
        c = AppErrorClassifier()
        g = c.classify("inst-1", "NotFoundError", "User not found")
        assert g.category == "not_found"

    def test_rate_limit(self):
        c = AppErrorClassifier()
        g = c.classify("inst-1", "RateLimitError", "Too many requests")
        assert g.category == "rate_limit"

    def test_internal(self):
        c = AppErrorClassifier()
        g = c.classify("inst-1", "RuntimeError", "Something broke")
        assert g.category == "internal"


class TestGetGroups:
    def test_sorted_by_count(self):
        c = AppErrorClassifier()
        c.classify("inst-1", "RuntimeError", "Error A", now=1000.0)
        for _ in range(5):
            c.classify("inst-1", "TimeoutError", "Timeout", now=1000.0)
        groups = c.get_groups("inst-1")
        assert groups[0].count == 5

    def test_filter_by_category(self):
        c = AppErrorClassifier()
        c.classify("inst-1", "TimeoutError", "Timeout")
        c.classify("inst-1", "AuthError", "Bad token")
        groups = c.get_groups("inst-1", category="network")
        assert len(groups) == 1

    def test_sorted_by_last_seen(self):
        c = AppErrorClassifier()
        c.classify("inst-1", "RuntimeError", "Old", now=1000.0)
        c.classify("inst-1", "TimeoutError", "New", now=2000.0)
        groups = c.get_groups("inst-1", sort_by="last_seen")
        assert groups[0].last_seen == 2000.0


class TestCategoryCounts:
    def test_counts(self):
        c = AppErrorClassifier()
        c.classify("inst-1", "TimeoutError", "A")
        c.classify("inst-1", "TimeoutError", "A")
        c.classify("inst-1", "AuthError", "B")
        counts = c.get_category_counts("inst-1")
        assert counts["network"] == 2
        assert counts["auth"] == 1


class TestTotalErrors:
    def test_total(self):
        c = AppErrorClassifier()
        c.classify("inst-1", "RuntimeError", "A")
        c.classify("inst-1", "RuntimeError", "A")
        c.classify("inst-1", "TimeoutError", "B")
        assert c.total_errors("inst-1") == 3


class TestIsolation:
    def test_cross_installation(self):
        c = AppErrorClassifier()
        c.classify("inst-1", "RuntimeError", "Error")
        assert c.total_errors("inst-2") == 0
