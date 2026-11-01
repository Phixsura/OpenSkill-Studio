from app.services.app_marketplace_app_app_support_ticket import create_ticket, build_ticket_queue

def test_create():
    r = create_ticket(subject="App crash", body="App crashes on login", priority="high")
    assert r["id"].startswith("TKT-")
    assert r["priority"] == "high"
    assert r["status"] == "open"

def test_queue():
    tickets = [
        {"status": "open", "priority": "urgent"},
        {"status": "in_progress", "priority": "high"},
        {"status": "resolved", "priority": "low"},
    ]
    r = build_ticket_queue(tickets=tickets)
    assert r["open"] == 2
    assert r["has_urgent"]
    assert r["total"] == 3
