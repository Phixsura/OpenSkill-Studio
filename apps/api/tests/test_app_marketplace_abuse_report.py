from app.services.app_marketplace_abuse_report import create_abuse_report, prioritize_report, resolve_report

def test_create_valid():
    r = create_abuse_report(reporter_id="u1", target_type="app", target_id="a1",
                             reason="spam", details="This app sends spam emails constantly")
    assert r["status"] == "open"
    assert r["error"] is None

def test_invalid_reason():
    r = create_abuse_report(reporter_id="u1", target_type="app", target_id="a1",
                             reason="invalid", details="some details here")
    assert r["error"]

def test_too_short():
    r = create_abuse_report(reporter_id="u1", target_type="app", target_id="a1",
                             reason="spam", details="short")
    assert "more details" in r["error"]

def test_priority_critical():
    p = prioritize_report(report={"target_id": "a1", "reason": "malware"}, existing_reports=[])
    assert p == "critical"

def test_priority_high():
    existing = [{"target_id": "a1"}, {"target_id": "a1"}, {"target_id": "a1"}]
    p = prioritize_report(report={"target_id": "a1", "reason": "spam"}, existing_reports=existing)
    assert p == "high"

def test_resolve():
    r = resolve_report(report={"target_id": "a1", "status": "open"}, action="remove_content", moderator_id="mod1")
    assert r["status"] == "resolved"
    assert r["resolution_action"] == "remove_content"
