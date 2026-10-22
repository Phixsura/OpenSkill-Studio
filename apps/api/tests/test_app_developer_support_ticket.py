from app.services.app_developer_support_ticket import create_ticket, get_open_tickets, get_ticket_stats

def test_create():
    t = create_ticket(developer_id="d1", subject="Bug", message="Something broken", priority="high")
    assert t["status"] == "open"
    assert t["priority"] == "high"

def test_open_tickets():
    create_ticket(developer_id="d2", subject="Help", message="Need help")
    tickets = get_open_tickets("d2")
    assert len(tickets) >= 1

def test_stats():
    create_ticket(developer_id="d3", subject="X", message="Y", priority="critical")
    s = get_ticket_stats()
    assert s["total_open"] >= 1
