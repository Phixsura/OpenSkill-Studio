from app.services.app_marketplace_app_app_app_app_app_app_app_notification_center import NotificationCenter

def test_notifications():
    nc = NotificationCenter()
    nc.send(user_id="u1", title="Welcome!", category="onboarding")
    nc.send(user_id="u1", title="Deploy complete", category="deploy")
    nc.send(user_id="u2", title="New follower", category="social")
    assert nc.unread_count("u1") == 2
    unread = nc.get_unread("u1")
    nc.mark_read("u1", unread[0]["id"])
    assert nc.unread_count("u1") == 1
    nc.mark_all_read("u1")
    assert nc.unread_count("u1") == 0
