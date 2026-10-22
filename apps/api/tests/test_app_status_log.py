from app.services.app_status_log import log_transition, get_transitions

def test_log_and_get():
    log_transition("sl1", "draft", "testing", "u1")
    assert len(get_transitions("sl1")) >= 1

def test_empty():
    assert get_transitions("nonexist") == []

def test_entry_fields():
    e = log_transition("sl2", "testing", "submitted", "u2")
    assert e["from"] == "testing" and e["to"] == "submitted"
