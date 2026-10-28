"""Tests for App Feature Gate — conditions, AND/OR, evaluation."""

import pytest

from app.services.app_feature_gate import AppFeatureGate


class TestDefineGate:
    def test_define(self):
        g = AppFeatureGate()
        gate = g.define_gate("inst-1", "premium-feature", "Premium Only",
                              [{"attribute": "plan", "operator": "eq", "value": "pro"}])
        assert gate.gate_id == "premium-feature"

    def test_empty_conditions(self):
        g = AppFeatureGate()
        with pytest.raises(ValueError):
            g.define_gate("inst-1", "g1", "X", [])


class TestEvaluate:
    def test_eq_pass(self):
        g = AppFeatureGate()
        g.define_gate("inst-1", "g1", "Test", [{"attribute": "plan", "operator": "eq", "value": "pro"}])
        assert g.evaluate("inst-1", "g1", {"plan": "pro"}) is True

    def test_eq_fail(self):
        g = AppFeatureGate()
        g.define_gate("inst-1", "g1", "Test", [{"attribute": "plan", "operator": "eq", "value": "pro"}])
        assert g.evaluate("inst-1", "g1", {"plan": "free"}) is False

    def test_in_operator(self):
        g = AppFeatureGate()
        g.define_gate("inst-1", "g1", "Test",
                       [{"attribute": "role", "operator": "in", "value": ["admin", "editor"]}])
        assert g.evaluate("inst-1", "g1", {"role": "admin"}) is True
        assert g.evaluate("inst-1", "g1", {"role": "viewer"}) is False

    def test_gte_operator(self):
        g = AppFeatureGate()
        g.define_gate("inst-1", "g1", "Test",
                       [{"attribute": "seats", "operator": "gte", "value": 10}])
        assert g.evaluate("inst-1", "g1", {"seats": 15}) is True
        assert g.evaluate("inst-1", "g1", {"seats": 5}) is False

    def test_missing_attribute(self):
        g = AppFeatureGate()
        g.define_gate("inst-1", "g1", "Test", [{"attribute": "plan", "operator": "eq", "value": "pro"}])
        assert g.evaluate("inst-1", "g1", {}) is False


class TestMatchModes:
    def test_and_mode(self):
        g = AppFeatureGate()
        g.define_gate("inst-1", "g1", "Test", [
            {"attribute": "plan", "operator": "eq", "value": "pro"},
            {"attribute": "role", "operator": "eq", "value": "admin"},
        ], match_all=True)
        assert g.evaluate("inst-1", "g1", {"plan": "pro", "role": "admin"}) is True
        assert g.evaluate("inst-1", "g1", {"plan": "pro", "role": "viewer"}) is False

    def test_or_mode(self):
        g = AppFeatureGate()
        g.define_gate("inst-1", "g1", "Test", [
            {"attribute": "plan", "operator": "eq", "value": "pro"},
            {"attribute": "role", "operator": "eq", "value": "admin"},
        ], match_all=False)
        assert g.evaluate("inst-1", "g1", {"plan": "free", "role": "admin"}) is True


class TestPassRate:
    def test_rate(self):
        g = AppFeatureGate()
        g.define_gate("inst-1", "g1", "Test", [{"attribute": "plan", "operator": "eq", "value": "pro"}])
        g.evaluate("inst-1", "g1", {"plan": "pro"})
        g.evaluate("inst-1", "g1", {"plan": "free"})
        assert g.pass_rate("inst-1", "g1") == 50.0


class TestIsolation:
    def test_cross_installation(self):
        g = AppFeatureGate()
        g.define_gate("inst-1", "g1", "Test", [{"attribute": "x", "operator": "eq", "value": 1}])
        with pytest.raises(KeyError):
            g.evaluate("inst-2", "g1", {})
