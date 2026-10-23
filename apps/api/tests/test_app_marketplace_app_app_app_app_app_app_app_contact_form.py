from app.services.app_marketplace_app_app_app_app_app_app_app_contact_form import validate_contact, process_contact

def test_valid():
    r = validate_contact(name="Alice", email="alice@test.com", topic="support",
                           message="I need help with my API integration please")
    assert r["valid"]

def test_invalid():
    r = validate_contact(name="A", email="bad", topic="nope", message="short")
    assert not r["valid"]
    assert len(r["errors"]) == 4

def test_process():
    r = process_contact(name="Bob", email="bob@test.com", topic="general",
                          message="Hello, I have a question about the platform")
    assert r["submitted"]
    assert "Bob" in r["confirmation"]
