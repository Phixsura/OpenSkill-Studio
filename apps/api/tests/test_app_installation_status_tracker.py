from app.services.app_installation_status_tracker import can_transition, record_transition, get_transitions

def test_valid_transition():
    assert can_transition("active", "suspended") is True

def test_invalid_transition():
    assert can_transition("active", "active") is False
    assert can_transition("uninstalled", "active") is False

def test_record():
    e = record_transition("ist1", from_status="active", to_status="suspended", reason="violation")
    assert e["from"] == "active"
    assert e["reason"] == "violation"

def test_get():
    record_transition("ist2", from_status="active", to_status="uninstalled")
    assert len(get_transitions("ist2")) >= 1

def test_empty():
    assert get_transitions("nobody") == []
