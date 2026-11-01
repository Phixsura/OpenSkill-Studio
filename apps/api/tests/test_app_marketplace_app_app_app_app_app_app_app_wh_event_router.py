from app.services.app_marketplace_app_app_app_app_app_app_app_wh_event_router import WebhookEventRouter

def test_route():
    wr = WebhookEventRouter()
    wr.register("order.created", "https://a.com/hook")
    wr.register("order.created", "https://b.com/hook")
    r = wr.route("order.created", {"id": "o1"})
    assert r["delivered_to"] == 2
    assert wr.stats()["total_delivered"] == 2

def test_unregister():
    wr = WebhookEventRouter()
    wr.register("user.signup", "https://a.com")
    wr.unregister("user.signup", "https://a.com")
    r = wr.route("user.signup", {})
    assert r["delivered_to"] == 0
