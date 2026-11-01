from app.services.app_marketplace_app_app_app_app_app_app_app_cl_subscribe import ChangelogSubscriptionManager

def test_subscribe():
    mgr = ChangelogSubscriptionManager()
    mgr.subscribe("app1", "alice")
    mgr.subscribe("app1", "bob")
    assert mgr.is_subscribed("app1", "alice")
    assert mgr.subscriber_count("app1") == 2
    mgr.unsubscribe("app1", "alice")
    assert not mgr.is_subscribed("app1", "alice")
    assert mgr.subscriber_count("app1") == 1
