from app.services.app_marketplace_support_ticket import create_ticket, update_ticket_status, get_ticket_stats

def test_create():
    r = create_ticket(subject="Cannot install app", description="Error on install page",
                      priority="high", reporter_id="u1", app_id="app1")
    assert r["ticket_id"].startswith("TKT-")
    assert r["priority_level"] == 3
    assert r["status"] == "open"

def test_create_invalid():
    r = create_ticket(subject="Hi", description="x", priority="medium", reporter_id="u1")
    assert "error" in r

def test_update():
    r = update_ticket_status(ticket_id="TKT-1", new_status="resolved", note="Fixed")
    assert r["updated"]

def test_stats():
    tickets = [{"status": "open", "priority": "high"}, {"status": "resolved", "priority": "low"},
               {"status": "in_progress", "priority": "medium"}]
    r = get_ticket_stats(tickets=tickets)
    assert r["total"] == 3
    assert r["open_count"] == 2
