from app.services.app_marketplace_app_app_contact_form import submit_contact

def test_valid():
    r = submit_contact(name="Alice", email="alice@example.com", topic="technical",
                       message="I need help with the webhook integration setup process")
    assert r["submitted"]
    assert r["ticket_id"].startswith("CTK-")

def test_invalid_email():
    r = submit_contact(name="X", email="bad", topic="general", message="A" * 20)
    assert not r["submitted"]

def test_short_message():
    r = submit_contact(name="X", email="a@b.com", topic="general", message="Hi")
    assert not r["submitted"]
    assert any("20" in e for e in r["errors"])
