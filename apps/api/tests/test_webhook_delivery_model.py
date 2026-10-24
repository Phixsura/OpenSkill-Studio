"""WebhookDelivery model tests."""

from app.models.webhook_delivery import AppWebhookDelivery, DeliveryStatus


def test_tablename():
    assert AppWebhookDelivery.__tablename__ == "app_webhook_deliveries"

def test_has_required_columns():
    cols = {c.name for c in AppWebhookDelivery.__table__.columns}
    required = {"id", "app_id", "event_type", "event_id", "url", "status", "created_at"}
    assert required.issubset(cols)

def test_has_optional_columns():
    cols = {c.name for c in AppWebhookDelivery.__table__.columns}
    optional = {"installation_id", "http_status", "attempt", "max_attempts", "error_message", "duration_ms", "delivered_at"}
    assert optional.issubset(cols)

def test_delivery_statuses():
    assert len(DeliveryStatus) == 4
    values = {s.value for s in DeliveryStatus}
    assert values == {"pending", "delivered", "failed", "retrying"}
