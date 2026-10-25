from app.services.app_marketplace_support_tickets import (
    SupportTicketService, TicketPriority, TicketStatus,
)


def test_create_and_list():
    sts = SupportTicketService()
    ticket = sts.create_ticket("t1", "ext-1", "user-1", "Bug report", "App crashes on load")
    assert ticket.status == TicketStatus.OPEN
    assert len(ticket.messages) == 1
    tickets = sts.list_tickets(extension_id="ext-1")
    assert len(tickets) == 1


def test_reply_and_status():
    sts = SupportTicketService()
    sts.create_ticket("t2", "ext-2", "user-2", "Help", "Need help configuring")
    sts.assign("t2", "dev-1")
    assert sts._tickets["t2"].status == TicketStatus.IN_PROGRESS
    sts.reply("t2", "dev-1", "What config are you using?")
    assert len(sts._tickets["t2"].messages) == 2


def test_resolve_and_close():
    sts = SupportTicketService()
    sts.create_ticket("t3", "ext-3", "user-3", "Question", "How to use?")
    sts.resolve("t3")
    assert sts._tickets["t3"].status == TicketStatus.RESOLVED
    sts.close("t3")
    assert sts._tickets["t3"].status == TicketStatus.CLOSED


def test_cannot_reply_closed():
    sts = SupportTicketService()
    sts.create_ticket("t4", "ext-4", "user-4", "Old", "old issue")
    sts.close("t4")
    assert sts.reply("t4", "user-4", "hello?") is False


def test_filter_by_assignee():
    sts = SupportTicketService()
    sts.create_ticket("t5", "ext-5", "u1", "A", "a")
    sts.create_ticket("t6", "ext-5", "u2", "B", "b")
    sts.assign("t5", "dev-x")
    assigned = sts.list_tickets(assigned_to="dev-x")
    assert len(assigned) == 1


def test_stats():
    sts = SupportTicketService()
    sts.create_ticket("s1", "ext-s", "u1", "A", "a")
    sts.create_ticket("s2", "ext-s", "u2", "B", "b")
    sts.resolve("s2")
    stats = sts.get_stats("ext-s")
    assert stats["total"] == 2
    assert stats["by_status"]["open"] == 1
    assert stats["by_status"]["resolved"] == 1
