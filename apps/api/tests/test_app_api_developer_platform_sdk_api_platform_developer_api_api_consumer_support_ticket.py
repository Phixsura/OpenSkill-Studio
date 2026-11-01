import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_support_ticket import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerSupportTicket, SupportTicket, TicketPriority, TicketStatus,
)

class TestConsumerSupportTicket:
    def test_create_and_open(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerSupportTicket()
        svc.create_ticket("inst-1", SupportTicket(ticket_id="t1", consumer_id="c1", subject="Can't authenticate", priority=TicketPriority.HIGH, category="integration"))
        open_t = svc.open_tickets("inst-1")
        assert len(open_t) == 1

    def test_resolve(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerSupportTicket()
        svc.create_ticket("inst-1", SupportTicket(ticket_id="t1", consumer_id="c1", subject="Bug"))
        svc.update_status("inst-1", "t1", TicketStatus.RESOLVED)
        assert len(svc.open_tickets("inst-1")) == 0

    def test_by_priority(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerSupportTicket()
        svc.create_ticket("inst-1", SupportTicket(ticket_id="t1", consumer_id="c1", subject="A", priority=TicketPriority.URGENT))
        svc.create_ticket("inst-1", SupportTicket(ticket_id="t2", consumer_id="c1", subject="B", priority=TicketPriority.LOW))
        p = svc.by_priority("inst-1")
        assert p["urgent"] == 1 and p["low"] == 1

    def test_invalid_category(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerSupportTicket()
        with pytest.raises(ValueError, match="Invalid category"):
            svc.create_ticket("inst-1", SupportTicket(ticket_id="t1", consumer_id="c1", subject="X", category="bad"))

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerSupportTicket()
        svc.create_ticket("inst-1", SupportTicket(ticket_id="t1", consumer_id="c1", subject="X"))
        assert len(svc.open_tickets("inst-2")) == 0
