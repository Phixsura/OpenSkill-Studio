from app.services.app_webhook_test import build_test_event, validate_test_target

def test_build():
    e = build_test_event()
    assert e["test"] is True
    assert e["event_type"] == "test.ping"

def test_validate_ok():
    assert validate_test_target("https://x.com") == []

def test_validate_empty():
    assert len(validate_test_target("")) > 0
