"""Tests for App A/B Test — create, assign, convert, results."""

import pytest

from app.services.app_ab_test import AppABTest

VARIANTS = [{"name": "control"}, {"name": "treatment"}]


class TestCreate:
    def test_create(self):
        a = AppABTest()
        exp = a.create("inst-1", "exp1", "Button Color", VARIANTS)
        assert len(exp.variants) == 2

    def test_too_few(self):
        a = AppABTest()
        with pytest.raises(ValueError, match="at least 2"):
            a.create("inst-1", "exp1", "Test", [{"name": "only"}])


class TestAssign:
    def test_deterministic(self):
        a = AppABTest()
        a.create("inst-1", "exp1", "Test", VARIANTS)
        v1 = a.assign("inst-1", "exp1", "user-123")
        v2 = a.assign("inst-1", "exp1", "user-123")
        assert v1 == v2

    def test_distribution(self):
        a = AppABTest()
        a.create("inst-1", "exp1", "Test", VARIANTS)
        results = set()
        for i in range(100):
            results.add(a.assign("inst-1", "exp1", f"user-{i}"))
        assert len(results) == 2  # both variants assigned

    def test_inactive(self):
        a = AppABTest()
        a.create("inst-1", "exp1", "Test", VARIANTS)
        a.deactivate("inst-1", "exp1")
        with pytest.raises(ValueError, match="not active"):
            a.assign("inst-1", "exp1", "user-1")


class TestConvert:
    def test_convert(self):
        a = AppABTest()
        a.create("inst-1", "exp1", "Test", VARIANTS)
        v = a.convert("inst-1", "exp1", "control")
        assert v.conversions == 1

    def test_results(self):
        a = AppABTest()
        a.create("inst-1", "exp1", "Test", VARIANTS)
        a.assign("inst-1", "exp1", "user-1")
        results = a.results("inst-1", "exp1")
        assert len(results) == 2


class TestIsolation:
    def test_cross(self):
        a = AppABTest()
        a.create("inst-1", "exp1", "Test", VARIANTS)
        assert a.list_experiments("inst-2") == []
