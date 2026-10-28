"""Tests for App A/B Test Manager — assignment, conversions, results."""

import pytest

from app.services.app_ab_test import AppABTestManager


VARIANTS = [{"name": "control", "weight": 1.0}, {"name": "treatment", "weight": 1.0}]


class TestCreateExperiment:
    def test_create(self):
        m = AppABTestManager()
        exp = m.create_experiment("inst-1", "exp-1", "Button Color", VARIANTS)
        assert exp.experiment_id == "exp-1"
        assert len(exp.variants) == 2

    def test_too_few_variants(self):
        m = AppABTestManager()
        with pytest.raises(ValueError, match="2 variants"):
            m.create_experiment("inst-1", "exp-1", "Test", [{"name": "only"}])

    def test_duplicate(self):
        m = AppABTestManager()
        m.create_experiment("inst-1", "exp-1", "Test", VARIANTS)
        with pytest.raises(ValueError, match="already exists"):
            m.create_experiment("inst-1", "exp-1", "Test2", VARIANTS)


class TestAssignment:
    def test_assign(self):
        m = AppABTestManager()
        m.create_experiment("inst-1", "exp-1", "Test", VARIANTS)
        a = m.assign("inst-1", "exp-1", "user-1")
        assert a.variant_name in ("control", "treatment")

    def test_sticky_assignment(self):
        m = AppABTestManager()
        m.create_experiment("inst-1", "exp-1", "Test", VARIANTS)
        a1 = m.assign("inst-1", "exp-1", "user-1")
        a2 = m.assign("inst-1", "exp-1", "user-1")
        assert a1.variant_name == a2.variant_name

    def test_deterministic(self):
        m1 = AppABTestManager()
        m2 = AppABTestManager()
        m1.create_experiment("inst-1", "exp-1", "Test", VARIANTS)
        m2.create_experiment("inst-1", "exp-1", "Test", VARIANTS)
        a1 = m1.assign("inst-1", "exp-1", "user-42")
        a2 = m2.assign("inst-1", "exp-1", "user-42")
        assert a1.variant_name == a2.variant_name

    def test_inactive_rejects(self):
        m = AppABTestManager()
        m.create_experiment("inst-1", "exp-1", "Test", VARIANTS)
        m.stop_experiment("inst-1", "exp-1")
        with pytest.raises(ValueError, match="not active"):
            m.assign("inst-1", "exp-1", "user-1")


class TestConversion:
    def test_record(self):
        m = AppABTestManager()
        m.create_experiment("inst-1", "exp-1", "Test", VARIANTS)
        m.assign("inst-1", "exp-1", "user-1")
        assert m.record_conversion("inst-1", "exp-1", "user-1") is True

    def test_unassigned_returns_false(self):
        m = AppABTestManager()
        m.create_experiment("inst-1", "exp-1", "Test", VARIANTS)
        assert m.record_conversion("inst-1", "exp-1", "nobody") is False


class TestResults:
    def test_results(self):
        m = AppABTestManager()
        m.create_experiment("inst-1", "exp-1", "Test", VARIANTS)
        for i in range(10):
            a = m.assign("inst-1", "exp-1", f"user-{i}")
        m.record_conversion("inst-1", "exp-1", "user-0")
        results = m.get_results("inst-1", "exp-1")
        assert results["name"] == "Test"
        total_exposures = sum(v["exposures"] for v in results["variants"])
        assert total_exposures == 10
        total_conversions = sum(v["conversions"] for v in results["variants"])
        assert total_conversions == 1


class TestStopExperiment:
    def test_stop(self):
        m = AppABTestManager()
        m.create_experiment("inst-1", "exp-1", "Test", VARIANTS)
        exp = m.stop_experiment("inst-1", "exp-1")
        assert exp.active is False


class TestIsolation:
    def test_cross_installation(self):
        m = AppABTestManager()
        m.create_experiment("inst-1", "exp-1", "Test", VARIANTS)
        with pytest.raises(KeyError):
            m.assign("inst-2", "exp-1", "user-1")
