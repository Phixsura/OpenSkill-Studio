from app.services.app_marketplace_support_ticket import create_ticket, add_reply, compute_response_metrics

def test_create():
    t = create_ticket(app_id="a1", user_id="u1", subject="Bug report", description="Crash on load", priority="high")
    assert t["status"] == "open"
    assert t["priority"] == "high"

def test_invalid_priority():
    t = create_ticket(app_id="a1", user_id="u1", subject="Test subject", description="D", priority="urgent")
    assert t["error"]

def test_short_subject():
    t = create_ticket(app_id="a1", user_id="u1", subject="Hi", description="D")
    assert "too short" in t["error"]

def test_reply():
    r = add_reply(ticket={"id": "t1"}, author_id="dev1", message="Working on it", is_developer=True)
    assert r["is_developer"]

def test_metrics():
    tickets = [{"status": "open"}, {"status": "resolved"}, {"status": "open"}]
    m = compute_response_metrics(tickets=tickets)
    assert m["open_count"] == 2
    assert m["resolved_count"] == 1
