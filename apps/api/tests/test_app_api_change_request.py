"""Tests for App API Change Request — submit, approve, implement."""

import pytest
from app.services.app_api_change_request import AppAPIChangeRequest, ChangeStatus


class TestSubmit:
    def test_submit(self):
        c = AppAPIChangeRequest()
        r = c.submit("inst-1", "cr1", "Add field", "Add email to User", "minor", "alice")
        assert r.status == ChangeStatus.PENDING

    def test_duplicate(self):
        c = AppAPIChangeRequest()
        c.submit("inst-1", "cr1", "A", "D", "none", "alice")
        with pytest.raises(ValueError):
            c.submit("inst-1", "cr1", "B", "D", "none", "bob")


class TestWorkflow:
    def test_approve_implement(self):
        c = AppAPIChangeRequest()
        c.submit("inst-1", "cr1", "A", "D", "major", "alice")
        c.approve("inst-1", "cr1", "bob")
        r = c.implement("inst-1", "cr1")
        assert r.status == ChangeStatus.IMPLEMENTED

    def test_reject(self):
        c = AppAPIChangeRequest()
        c.submit("inst-1", "cr1", "A", "D", "breaking", "alice")
        r = c.reject("inst-1", "cr1", "bob")
        assert r.status == ChangeStatus.REJECTED

    def test_cannot_implement_pending(self):
        c = AppAPIChangeRequest()
        c.submit("inst-1", "cr1", "A", "D", "none", "alice")
        with pytest.raises(ValueError):
            c.implement("inst-1", "cr1")


class TestIsolation:
    def test_cross(self):
        c = AppAPIChangeRequest()
        c.submit("inst-1", "cr1", "A", "D", "none", "alice")
        assert c.list_requests("inst-2") == []
