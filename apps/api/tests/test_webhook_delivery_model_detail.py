"""AppWebhookDelivery model detail tests."""

import pytest
from app.models.webhook_delivery import AppWebhookDelivery

def test_has_app_id_fk():
    assert len(AppWebhookDelivery.__table__.columns["app_id"].foreign_keys) > 0

def test_url_not_nullable():
    assert not AppWebhookDelivery.__table__.columns["url"].nullable

def test_event_type_not_nullable():
    assert not AppWebhookDelivery.__table__.columns["event_type"].nullable

def test_has_max_attempts():
    assert "max_attempts" in {c.name for c in AppWebhookDelivery.__table__.columns}

def test_has_error_message():
    assert "error_message" in {c.name for c in AppWebhookDelivery.__table__.columns}

def test_has_delivered_at():
    assert "delivered_at" in {c.name for c in AppWebhookDelivery.__table__.columns}
