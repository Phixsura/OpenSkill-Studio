"""Tests for App Release Gate — gates, approval, blocking."""

import pytest

from app.services.app_release_gate import AppReleaseGate, GateStatus

GATES = [
    {"gate_id": "tests", "name": "Unit Tests", "required": True},
    {"gate_id": "coverage", "name": "Code Coverage", "required": True},
    {"gate_id": "review", "name": "Peer Review", "required": True},
    {"gate_id": "docs", "name": "Docs Updated", "required": False},
]


class TestCreateGates:
    def test_create(self):
        g = AppReleaseGate()
        r = g.create_release_gates("inst-1", "2.0.0", GATES)
        assert r.version == "2.0.0"
        assert len(r.gates) == 4

    def test_empty_gates(self):
        g = AppReleaseGate()
        with pytest.raises(ValueError, match="at least one"):
            g.create_release_gates("inst-1", "1.0.0", [])

    def test_duplicate(self):
        g = AppReleaseGate()
        g.create_release_gates("inst-1", "1.0.0", GATES)
        with pytest.raises(ValueError, match="already exist"):
            g.create_release_gates("inst-1", "1.0.0", GATES)


class TestUpdateGate:
    def test_pass(self):
        g = AppReleaseGate()
        g.create_release_gates("inst-1", "1.0.0", GATES)
        gc = g.update_gate("inst-1", "1.0.0", "tests", GateStatus.PASSED)
        assert gc.status == GateStatus.PASSED

    def test_fail(self):
        g = AppReleaseGate()
        g.create_release_gates("inst-1", "1.0.0", GATES)
        gc = g.update_gate("inst-1", "1.0.0", "tests", GateStatus.FAILED, "3 tests failed")
        assert gc.message == "3 tests failed"

    def test_unknown_gate(self):
        g = AppReleaseGate()
        g.create_release_gates("inst-1", "1.0.0", GATES)
        with pytest.raises(KeyError, match="Gate"):
            g.update_gate("inst-1", "1.0.0", "nope", GateStatus.PASSED)


class TestApproval:
    def test_approved_when_all_required_pass(self):
        g = AppReleaseGate()
        g.create_release_gates("inst-1", "1.0.0", GATES)
        g.update_gate("inst-1", "1.0.0", "tests", GateStatus.PASSED)
        g.update_gate("inst-1", "1.0.0", "coverage", GateStatus.PASSED)
        g.update_gate("inst-1", "1.0.0", "review", GateStatus.PASSED)
        assert g.check_approval("inst-1", "1.0.0") is True

    def test_blocked_when_required_pending(self):
        g = AppReleaseGate()
        g.create_release_gates("inst-1", "1.0.0", GATES)
        g.update_gate("inst-1", "1.0.0", "tests", GateStatus.PASSED)
        assert g.check_approval("inst-1", "1.0.0") is False

    def test_blocked_when_required_failed(self):
        g = AppReleaseGate()
        g.create_release_gates("inst-1", "1.0.0", GATES)
        g.update_gate("inst-1", "1.0.0", "tests", GateStatus.PASSED)
        g.update_gate("inst-1", "1.0.0", "coverage", GateStatus.FAILED)
        g.update_gate("inst-1", "1.0.0", "review", GateStatus.PASSED)
        assert g.check_approval("inst-1", "1.0.0") is False

    def test_optional_gate_doesnt_block(self):
        g = AppReleaseGate()
        g.create_release_gates("inst-1", "1.0.0", GATES)
        g.update_gate("inst-1", "1.0.0", "tests", GateStatus.PASSED)
        g.update_gate("inst-1", "1.0.0", "coverage", GateStatus.PASSED)
        g.update_gate("inst-1", "1.0.0", "review", GateStatus.PASSED)
        # docs is optional, still pending
        assert g.check_approval("inst-1", "1.0.0") is True


class TestFailedGates:
    def test_list_failed(self):
        g = AppReleaseGate()
        g.create_release_gates("inst-1", "1.0.0", GATES)
        g.update_gate("inst-1", "1.0.0", "tests", GateStatus.FAILED)
        r = g.get_result("inst-1", "1.0.0")
        assert len(r.failed_gates) == 1
        assert r.failed_gates[0].gate_id == "tests"


class TestIsolation:
    def test_cross_installation(self):
        g = AppReleaseGate()
        g.create_release_gates("inst-1", "1.0.0", GATES)
        with pytest.raises(KeyError):
            g.get_result("inst-2", "1.0.0")
