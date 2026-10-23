from app.services.app_marketplace_app_app_app_app_app_app_app_api_changelog_sub import create_subscription, build_notification

def test_subscription():
    sub = create_subscription(email="dev@test.com", api_versions=["v1", "v2"])
    assert sub["active"]
    assert sub["preferences"]["breaking"]

def test_notification():
    sub = create_subscription(email="dev@test.com", api_versions=["v1"],
                                notify_breaking=True, notify_new=False)
    changes = [
        {"type": "breaking", "title": "Removed field", "version": "v2"},
        {"type": "new", "title": "New endpoint", "version": "v2"},
        {"type": "deprecation", "title": "Old method", "version": "v1"},
    ]
    r = build_notification(changes, sub)
    assert r["count"] == 2  # breaking + deprecation
    assert r["should_send"]
