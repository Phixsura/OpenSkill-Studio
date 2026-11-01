from app.services.app_marketplace_app_app_app_app_app_app_app_wh_sub_mgr import WebhookSubscriptionManager

def test_subscribe_dispatch():
    wm = WebhookSubscriptionManager()
    wm.subscribe("s1", "https://a.com/hook", ["order.created", "order.paid"])
    wm.subscribe("s2", "https://b.com/hook", ["order.created"])
    r = wm.dispatch("order.created")
    assert r["dispatched_to"] == 2
    r2 = wm.dispatch("order.paid")
    assert r2["dispatched_to"] == 1

def test_unsubscribe():
    wm = WebhookSubscriptionManager()
    wm.subscribe("s1", "https://a.com", ["x"])
    wm.unsubscribe("s1")
    r = wm.dispatch("x")
    assert r["dispatched_to"] == 0
    assert wm.stats()["active"] == 0
