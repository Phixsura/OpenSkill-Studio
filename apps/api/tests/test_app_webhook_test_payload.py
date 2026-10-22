from app.services.app_webhook_test_payload import generate_test_payload, list_testable_events

def test_known_event():
    p = generate_test_payload("submission.completed")
    assert "submission_id" in p
    assert p["test"] is True

def test_unknown_event():
    p = generate_test_payload("custom.event")
    assert p["test"] is True

def test_unique_ids():
    p1 = generate_test_payload("submission.completed")
    p2 = generate_test_payload("submission.completed")
    assert p1["submission_id"] != p2["submission_id"]

def test_list():
    events = list_testable_events()
    assert "submission.completed" in events
    assert len(events) >= 4
