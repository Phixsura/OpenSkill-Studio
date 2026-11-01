from app.services.app_marketplace_extension_support_ticket import ExtSupportTicketService

def test_create_and_reply():
    svc = ExtSupportTicketService()
    t = svc.create("ext-1", "u1", "Bug report", "Found a bug", "high")
    assert len(t.messages) == 1
    svc.reply(t.ticket_id, "dev-1", "Thanks, looking into it")
    assert len(t.messages) == 2
    assert t.status == "in_progress"

def test_no_reply_closed():
    svc = ExtSupportTicketService()
    t = svc.create("ext-1", "u1", "Issue", "Help")
    svc.update_status(t.ticket_id, "closed")
    assert svc.reply(t.ticket_id, "dev-1", "reply") is False

def test_priority_sort():
    svc = ExtSupportTicketService()
    svc.create("ext-1", "u1", "Low", "l", "low")
    svc.create("ext-1", "u2", "Urgent", "u", "urgent")
    svc.create("ext-1", "u3", "Normal", "n", "normal")
    tickets = svc.get_by_extension("ext-1")
    assert tickets[0].priority == "urgent"
