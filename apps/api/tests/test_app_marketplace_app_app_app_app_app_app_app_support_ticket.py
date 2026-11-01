from app.services.app_marketplace_app_app_app_app_app_app_app_support_ticket import SupportTicketSystem

def test_tickets():
    sys = SupportTicketSystem()
    t = sys.create(title="Login broken", description="Can't log in", priority="high", user_id="alice")
    assert t["id"] == "TKT-0001"
    sys.reply(t["id"], message="Looking into it", author="support")
    sys.reply(t["id"], message="Fixed now", author="support")
    sys.resolve(t["id"])
    tickets = sys.list_tickets()
    assert tickets[0]["status"] == "resolved"
    assert tickets[0]["replies"] == 2
    s = sys.stats()
    assert s["total"] == 1
    assert s["resolved"] == 1
