"""Webhook delivery status + model field coverage."""

import pytest
from app.models.webhook_delivery import AppWebhookDelivery, DeliveryStatus

STATUS_VALUES = ["pending", "delivered", "failed", "retrying"]

@pytest.mark.parametrize("status", STATUS_VALUES)
def test_status_value(status):
    assert status in {s.value for s in DeliveryStatus}

def test_status_count():
    assert len(DeliveryStatus) == 4

STATUS_TRANSITIONS = [
    ("pending", "delivered"),
    ("pending", "failed"),
    ("pending", "retrying"),
    ("retrying", "delivered"),
    ("retrying", "failed"),
]

@pytest.mark.parametrize("src,dst", STATUS_TRANSITIONS)
def test_valid_delivery_transitions(src, dst):
    """Document expected delivery status transitions."""
    assert src in {s.value for s in DeliveryStatus}
    assert dst in {s.value for s in DeliveryStatus}

def test_model_has_duration():
    cols = {c.name for c in AppWebhookDelivery.__table__.columns}
    assert "duration_ms" in cols

def test_model_has_http_status():
    cols = {c.name for c in AppWebhookDelivery.__table__.columns}
    assert "http_status" in cols

def test_model_has_attempt():
    cols = {c.name for c in AppWebhookDelivery.__table__.columns}
    assert "attempt" in cols
