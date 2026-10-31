from app.services.app_marketplace_app_app_app_app_app_app_app_webhook_catalog import WebhookEventCatalog

def test_catalog():
    c = WebhookEventCatalog()
    c.register("app.installed", description="App installed by user",
                payload_schema={"required": ["app_id", "user_id"]}, category="apps")
    c.register("payment.completed", description="Payment succeeded",
                payload_schema={"required": ["payment_id", "amount"]}, category="billing")
    v = c.validate_payload("app.installed", {"app_id": "a1", "user_id": "u1"})
    assert v["valid"]
    v2 = c.validate_payload("app.installed", {"app_id": "a1"})
    assert not v2["valid"]
    assert "user_id" in v2["missing_fields"]
    events = c.list_events(category="apps")
    assert len(events) == 1
    assert c.categories() == ["apps", "billing"]
