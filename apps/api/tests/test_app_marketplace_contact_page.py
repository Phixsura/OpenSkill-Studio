from app.services.app_marketplace_contact_page import build_contact_page, submit_contact_form

def test_page():
    p = build_contact_page()
    assert p["page_type"] == "contact"
    assert len(p["channels"]) == 4
    assert len(p["form"]["fields"]) == 4

def test_submit():
    r = submit_contact_form(name="Alice", email="alice@test.com", subject="General", message="Hello!")
    assert r["success"]
    assert "TICKET-" in r["ticket_id"]

def test_submit_invalid():
    r = submit_contact_form(name="", email="", subject="", message="")
    assert not r["success"]
