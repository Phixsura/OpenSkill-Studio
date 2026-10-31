"""Tests for App API Support Ticket — create, assign, resolve."""

import pytest
from app.services.app_api_support_ticket import AppAPISupportTicket, TicketPriority, TicketStatus


class TestCreate:
    def test_create(self):
        s = AppAPISupportTicket()
        t = s.create("inst-1", "t1", "Cannot authenticate", "alice", TicketPriority.HIGH)
        assert t.status == TicketStatus.OPEN

    def test_duplicate(self):
        s = AppAPISupportTicket()
        s.create("inst-1", "t1", "A", "a", TicketPriority.LOW)
        with pytest.raises(ValueError):
            s.create("inst-1", "t1", "B", "b", TicketPriority.LOW)


class TestLifecycle:
    def test_assign_resolve(self):
        s = AppAPISupportTicket()
        s.create("inst-1", "t1", "Issue", "alice", TicketPriority.MEDIUM)
        s.assign("inst-1", "t1", "bob")
        t = s.resolve("inst-1", "t1")
        assert t.status == TicketStatus.RESOLVED
        assert t.resolved_at is not None

    def test_open_tickets(self):
        s = AppAPISupportTicket()
        s.create("inst-1", "t1", "A", "a", TicketPriority.LOW)
        s.create("inst-1", "t2", "B", "b", TicketPriority.HIGH)
        s.resolve("inst-1", "t1")
        assert len(s.open_tickets("inst-1")) == 1


class TestIsolation:
    def test_cross(self):
        s = AppAPISupportTicket()
        s.create("inst-1", "t1", "A", "a", TicketPriority.LOW)
        assert s.list_tickets("inst-2") == []
