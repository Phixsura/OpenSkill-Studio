from app.services.app_marketplace_app_app_app_app_app_app_app_wh_event_filter import WebhookEventFilter

def test_filter():
    wef = WebhookEventFilter()
    wef.add_filter("sub-1", ["order.created", "order.paid"])
    assert wef.should_deliver("sub-1", "order.created")["deliver"]
    assert not wef.should_deliver("sub-1", "user.signup")["deliver"]

def test_payload_filter():
    wef = WebhookEventFilter()
    wef.add_filter("sub-1", ["*"], include_fields=["id", "status"])
    filtered = wef.filter_payload("sub-1", {"id": "o1", "status": "paid", "amount": 100, "secret": "x"})
    assert "id" in filtered
    assert "status" in filtered
    assert "secret" not in filtered
