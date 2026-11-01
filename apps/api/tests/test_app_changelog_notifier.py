from app.services.app_changelog_notifier import build_upgrade_notification, should_auto_upgrade

def test_normal_notification():
    n = build_upgrade_notification(app_name="My App", from_version="1.0", to_version="2.0")
    assert "Update available" in n["title"]
    assert n["urgency"] == "normal"

def test_breaking_notification():
    n = build_upgrade_notification(app_name="X", from_version="1.0", to_version="2.0", breaking=True)
    assert "Breaking" in n["title"]
    assert n["urgency"] == "high"

def test_with_changelog():
    n = build_upgrade_notification(app_name="X", from_version="1.0", to_version="2.0", changelog="Added webhooks")
    assert "webhooks" in n["body"]

def test_auto_upgrade_ok():
    assert should_auto_upgrade(breaking=False) is True

def test_no_auto_upgrade_breaking():
    assert should_auto_upgrade(breaking=True) is False

def test_no_auto_upgrade_disabled():
    assert should_auto_upgrade(breaking=False, org_auto_upgrade=False) is False
