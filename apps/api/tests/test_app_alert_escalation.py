"""Tests for App Alert Escalation — tiers, escalation, acknowledgment."""

import pytest

from app.services.app_alert_escalation import AppAlertEscalation

TIERS = [
    {"name": "On-call", "targets": ["oncall@x.com"], "timeout_seconds": 300},
    {"name": "Manager", "targets": ["mgr@x.com"], "timeout_seconds": 600},
    {"name": "VP Eng", "targets": ["vp@x.com"], "timeout_seconds": 900},
]


class TestDefine:
    def test_define_tiers(self):
        e = AppAlertEscalation()
        tiers = e.define_tiers("inst-1", TIERS)
        assert len(tiers) == 3
        assert tiers[0].name == "On-call"

    def test_empty_tiers(self):
        e = AppAlertEscalation()
        with pytest.raises(ValueError):
            e.define_tiers("inst-1", [])


class TestEscalation:
    def test_no_escalation_in_window(self):
        e = AppAlertEscalation()
        e.define_tiers("inst-1", TIERS)
        e.create_alert("inst-1", "a1", now=1000.0)
        result = e.check_escalation("inst-1", "a1", now=1100.0)
        assert result is None

    def test_escalate_to_tier_1(self):
        e = AppAlertEscalation()
        e.define_tiers("inst-1", TIERS)
        e.create_alert("inst-1", "a1", now=1000.0)
        result = e.check_escalation("inst-1", "a1", now=1301.0)
        assert result is not None
        assert result.name == "Manager"

    def test_escalate_to_tier_2(self):
        e = AppAlertEscalation()
        e.define_tiers("inst-1", TIERS)
        e.create_alert("inst-1", "a1", now=1000.0)
        e.check_escalation("inst-1", "a1", now=1301.0)  # → tier 1
        result = e.check_escalation("inst-1", "a1", now=1902.0)  # → tier 2
        assert result is not None
        assert result.name == "VP Eng"


class TestAcknowledge:
    def test_acknowledge(self):
        e = AppAlertEscalation()
        e.define_tiers("inst-1", TIERS)
        e.create_alert("inst-1", "a1")
        a = e.acknowledge("inst-1", "a1", by="alice")
        assert a.acknowledged is True

    def test_acknowledged_no_escalation(self):
        e = AppAlertEscalation()
        e.define_tiers("inst-1", TIERS)
        e.create_alert("inst-1", "a1", now=1000.0)
        e.acknowledge("inst-1", "a1", by="alice")
        result = e.check_escalation("inst-1", "a1", now=9999.0)
        assert result is None

    def test_not_found(self):
        e = AppAlertEscalation()
        with pytest.raises(KeyError):
            e.acknowledge("inst-1", "nope", "alice")


class TestIsolation:
    def test_cross_installation(self):
        e = AppAlertEscalation()
        e.create_alert("inst-1", "a1")
        with pytest.raises(KeyError):
            e.get_alert("inst-2", "a1")
