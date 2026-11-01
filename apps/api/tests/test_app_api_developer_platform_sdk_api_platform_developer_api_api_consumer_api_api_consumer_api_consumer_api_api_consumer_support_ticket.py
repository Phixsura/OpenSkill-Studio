import pytest
from datetime import datetime
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_api_consumer_support_ticket import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerSupportTicket, SupportTicket, TicketReply,
)

class TestConsumerApiSupportTicket:
    def _now(self):
        return datetime(2026, 6, 1)

    def test_create_and_list(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerSupportTicket()
        svc.create("inst-1", SupportTicket(ticket_id="t1", consumer_id="c1", subject="API Error", description="500 on /api", priority="high", created_at=self._now()))
        tickets = svc.list_tickets("inst-1", consumer_id="c1")
        assert len(tickets) == 1 and tickets[0].status == "open"

    def test_update_status(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerSupportTicket()
        svc.create("inst-1", SupportTicket(ticket_id="t1", consumer_id="c1", subject="Bug", description="x", created_at=self._now()))
        svc.update_status("inst-1", "t1", "resolved", now=self._now())
        tickets = svc.list_tickets("inst-1", status="resolved")
        assert len(tickets) == 1 and tickets[0].resolved_at is not None

    def test_add_reply(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerSupportTicket()
        svc.create("inst-1", SupportTicket(ticket_id="t1", consumer_id="c1", subject="Q", description="x", created_at=self._now()))
        svc.add_reply("inst-1", TicketReply(reply_id="r1", ticket_id="t1", author="support", message="Looking into it", is_staff=True, created_at=self._now()))
        replies = svc.get_replies("inst-1", "t1")
        assert len(replies) == 1 and replies[0].is_staff

    def test_priority_sorting(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerSupportTicket()
        svc.create("inst-1", SupportTicket(ticket_id="t1", consumer_id="c1", subject="Low", description="x", priority="low", created_at=self._now()))
        svc.create("inst-1", SupportTicket(ticket_id="t2", consumer_id="c1", subject="Urgent", description="x", priority="urgent", created_at=self._now()))
        tickets = svc.list_tickets("inst-1")
        assert tickets[0].priority == "urgent"

    def test_invalid_priority(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerSupportTicket()
        with pytest.raises(ValueError, match="Invalid priority"):
            svc.create("inst-1", SupportTicket(ticket_id="t1", consumer_id="c1", subject="X", description="x", priority="critical"))

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerSupportTicket()
        svc.create("inst-1", SupportTicket(ticket_id="t1", consumer_id="c1", subject="X", description="x", created_at=self._now()))
        assert len(svc.list_tickets("inst-2")) == 0
