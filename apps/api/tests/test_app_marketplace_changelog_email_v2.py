from app.services.app_marketplace_changelog_email_v2 import build_changelog_email_v2, should_send_email

def test_email():
    e = build_changelog_email_v2(
        app={"name": "MyApp", "slug": "my-app"}, version={"version": "2.0"},
        changes=[{"type": "feat", "description": "Dark mode", "breaking": False},
                 {"type": "fix", "description": "Login bug"}],
        recipients={"all_users": 500, "active_users": 300})
    assert "New Features" in e["subject"]
    assert e["total_changes"] == 2
    assert e["recipients"]["targeted"] == 300

def test_breaking():
    e = build_changelog_email_v2(
        app={"name": "App", "slug": "app"}, version={"version": "3.0"},
        changes=[{"type": "feat", "description": "X", "breaking": True}],
        recipients={"all_users": 100, "active_users": 50})
    assert "Breaking" in e["subject"]

def test_should_send():
    r = should_send_email(changes=[{"type": "feat"}, {"type": "fix"}])
    assert r["send"]
    assert r["reason"] == "features"

def test_should_not_send():
    r = should_send_email(changes=[{"type": "chore"}])
    assert not r["send"]
