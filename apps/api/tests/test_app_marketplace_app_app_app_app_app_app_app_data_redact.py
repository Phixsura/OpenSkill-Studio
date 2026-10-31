from app.services.app_marketplace_app_app_app_app_app_app_app_data_redact import redact_text, redact_dict

def test_redact_text():
    r = redact_text("Contact alice@example.com or 555-123-4567")
    assert "[EMAIL]" in r["text"]
    assert "[PHONE]" in r["text"]
    assert r["redactions"] == 2

def test_redact_ssn():
    r = redact_text("SSN: 123-45-6789")
    assert "[SSN]" in r["text"]

def test_redact_dict():
    r = redact_dict(
        {"name": "Alice", "email": "alice@test.com", "password": "secret123", "notes": "Call 555-000-1234"},
        sensitive_keys=["password"])
    assert r["data"]["password"] == "***REDACTED***"
    assert "[EMAIL]" in r["data"]["email"]
    assert "[PHONE]" in r["data"]["notes"]
