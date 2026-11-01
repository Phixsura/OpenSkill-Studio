from app.services.app_developer_welcome_email import build_welcome_email

def test_email():
    e = build_welcome_email("Bob", "bob-dev")
    assert "Bob" in e["subject"]
    assert "Get Started" in e["cta"]["label"]
