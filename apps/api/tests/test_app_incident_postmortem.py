"""Tests for App Incident Postmortem — create, actions, completion."""

import pytest

from app.services.app_incident_postmortem import AppIncidentPostmortem

ACTIONS = [
    {"action_id": "a1", "description": "Add monitoring", "owner": "alice"},
    {"action_id": "a2", "description": "Fix retry logic", "owner": "bob"},
]


class TestCreate:
    def test_create(self):
        p = AppIncidentPostmortem()
        pm = p.create_postmortem("inst-1", "pm1", "inc-1", "DB Outage",
                                  "Database went down", "Connection pool leak", "2h downtime",
                                  action_items=ACTIONS)
        assert pm.root_cause == "Connection pool leak"
        assert len(pm.action_items) == 2

    def test_missing_root_cause(self):
        p = AppIncidentPostmortem()
        with pytest.raises(ValueError, match="root_cause"):
            p.create_postmortem("inst-1", "pm1", "inc-1", "T", "S", "", "I")


class TestActions:
    def test_complete(self):
        p = AppIncidentPostmortem()
        p.create_postmortem("inst-1", "pm1", "inc-1", "T", "S", "RC", "I", ACTIONS)
        a = p.complete_action("inst-1", "pm1", "a1")
        assert a.completed is True

    def test_unknown_action(self):
        p = AppIncidentPostmortem()
        p.create_postmortem("inst-1", "pm1", "inc-1", "T", "S", "RC", "I")
        with pytest.raises(KeyError):
            p.complete_action("inst-1", "pm1", "nope")


class TestCompletion:
    def test_completion_pct(self):
        p = AppIncidentPostmortem()
        p.create_postmortem("inst-1", "pm1", "inc-1", "T", "S", "RC", "I", ACTIONS)
        p.complete_action("inst-1", "pm1", "a1")
        pm = p.get_postmortem("inst-1", "pm1")
        assert pm.completion_pct == 50.0

    def test_no_actions_is_100(self):
        p = AppIncidentPostmortem()
        p.create_postmortem("inst-1", "pm1", "inc-1", "T", "S", "RC", "I")
        assert p.get_postmortem("inst-1", "pm1").completion_pct == 100.0


class TestIsolation:
    def test_cross_installation(self):
        p = AppIncidentPostmortem()
        p.create_postmortem("inst-1", "pm1", "inc-1", "T", "S", "RC", "I")
        with pytest.raises(KeyError):
            p.get_postmortem("inst-2", "pm1")
