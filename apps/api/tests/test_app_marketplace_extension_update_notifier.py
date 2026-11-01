from app.services.app_marketplace_extension_update_notifier import ExtUpdateNotifierService

def test_subscribe_and_notify():
    svc = ExtUpdateNotifierService()
    svc.subscribe("u1", "ext-1")
    svc.subscribe("u2", "ext-1")
    notif = svc.publish_update("ext-1", "1.0", "2.0", ["New feature"])
    assert len(notif.notified_users) == 2
    assert len(svc.get_user_updates("u1")) == 1

def test_breaking_updates():
    svc = ExtUpdateNotifierService()
    svc.subscribe("u1", "ext-1")
    svc.publish_update("ext-1", "1.0", "2.0", ["Breaking change"], breaking=True)
    svc.publish_update("ext-1", "2.0", "2.1", ["Patch"])
    assert len(svc.get_breaking_updates("u1")) == 1

def test_unsubscribe():
    svc = ExtUpdateNotifierService()
    svc.subscribe("u1", "ext-1")
    svc.unsubscribe("u1", "ext-1")
    svc.publish_update("ext-1", "1.0", "2.0", ["Update"])
    assert len(svc.get_user_updates("u1")) == 0
