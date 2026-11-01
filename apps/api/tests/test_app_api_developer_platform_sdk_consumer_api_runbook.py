"""Tests for Consumer API Runbook service."""
import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_runbook import (
    RunbookManager, Runbook, RunbookStep,
)


class TestRunbookManager:
    def _make_runbook(self):
        return Runbook("rb1", "Incident Response", "incident", [
            RunbookStep("s1", "Check Logs", order=1),
            RunbookStep("s2", "Restart Service", order=2),
            RunbookStep("s3", "Verify Health", order=3),
        ])

    def test_create_runbook(self):
        svc = RunbookManager()
        result = svc.create_runbook(self._make_runbook())
        assert result["steps"] == 3

    def test_start_and_complete(self):
        svc = RunbookManager()
        svc.create_runbook(self._make_runbook())
        svc.start_execution("ex1", "rb1")
        svc.complete_step("ex1", "s1", True, "Logs look normal")
        svc.complete_step("ex1", "s2", True, "Restarted OK")
        result = svc.complete_step("ex1", "s3", True, "Health OK")
        assert result["status"] == "completed"

    def test_step_failure(self):
        svc = RunbookManager()
        svc.create_runbook(self._make_runbook())
        svc.start_execution("ex1", "rb1")
        result = svc.complete_step("ex1", "s1", False, "Error found")
        assert result["status"] == "failed"

    def test_abort(self):
        svc = RunbookManager()
        svc.create_runbook(self._make_runbook())
        svc.start_execution("ex1", "rb1")
        result = svc.abort("ex1")
        assert result["status"] == "aborted"

    def test_get_execution(self):
        svc = RunbookManager()
        svc.create_runbook(self._make_runbook())
        svc.start_execution("ex1", "rb1")
        svc.complete_step("ex1", "s1")
        ex = svc.get_execution("ex1")
        assert ex["progress"] == "1/3"

    def test_list_runbooks(self):
        svc = RunbookManager()
        svc.create_runbook(self._make_runbook())
        books = svc.list_runbooks()
        assert len(books) == 1
        assert books[0]["name"] == "Incident Response"

    def test_stats(self):
        svc = RunbookManager()
        svc.create_runbook(self._make_runbook())
        svc.start_execution("ex1", "rb1")
        for s in ["s1", "s2", "s3"]:
            svc.complete_step("ex1", s)
        svc.start_execution("ex2", "rb1")
        svc.complete_step("ex2", "s1", False)
        stats = svc.get_stats()
        assert stats["completed"] == 1
        assert stats["failed"] == 1

    def test_empty_runbook_rejected(self):
        svc = RunbookManager()
        with pytest.raises(ValueError):
            svc.create_runbook(Runbook("rb1", "Empty", steps=[]))

    def test_duplicate_runbook(self):
        svc = RunbookManager()
        svc.create_runbook(self._make_runbook())
        with pytest.raises(ValueError):
            svc.create_runbook(self._make_runbook())

    def test_isolation(self):
        a, b = RunbookManager(), RunbookManager()
        a.create_runbook(self._make_runbook())
        assert b.list_runbooks() == []
