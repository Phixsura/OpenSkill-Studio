import pytest
from app.services.app_api_developer_api_api_developer_api_api_developer_support_ticket import AppAPIDeveloperAPIApiDeveloperApiApiDeveloperSupportTicket

class TestSupportTicket:
    def test_create(self):
        s = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperSupportTicket()
        t = s.create("inst-1", "t1", "dev1", "Auth broken", "Cannot authenticate", "high")
        assert t.status == "open"

    def test_resolve(self):
        s = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperSupportTicket()
        s.create("inst-1", "t1", "dev1", "Bug", "Desc")
        t = s.update_status("inst-1", "t1", "resolved")
        assert t.resolution_time_hours is not None

    def test_open_tickets(self):
        s = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperSupportTicket()
        s.create("inst-1", "t1", "d1", "A", "B")
        s.create("inst-1", "t2", "d2", "C", "D")
        s.update_status("inst-1", "t1", "closed")
        assert len(s.open_tickets("inst-1")) == 1

    def test_by_priority(self):
        s = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperSupportTicket()
        s.create("inst-1", "t1", "d1", "A", "B", "urgent")
        s.create("inst-1", "t2", "d2", "C", "D", "low")
        p = s.by_priority("inst-1")
        assert p["urgent"] == 1

    def test_isolation(self):
        s = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperSupportTicket()
        s.create("inst-1", "t1", "d1", "A", "B")
        assert len(s.open_tickets("inst-2")) == 0
