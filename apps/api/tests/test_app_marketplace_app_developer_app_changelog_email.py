from app.services.app_marketplace_app_developer_app_changelog_email import build_changelog_email, should_send_notification

def test_email():
    e = build_changelog_email(app_name="MyApp", version="2.0",
                               changes=[{"type": "features", "description": "Dark mode"},
                                        {"type": "fixes", "description": "Login bug"}],
                               recipients=100)
    assert "v2.0" in e["subject"]
    assert e["recipients"] == 100
    assert e["has_features"]

def test_should_send():
    r = should_send_notification(change_types=["features", "fixes"])
    assert r["should_send"]

def test_should_not_send():
    r = should_send_notification(change_types=["docs", "chore"])
    assert not r["should_send"]
