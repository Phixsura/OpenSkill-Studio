"""Parametrized tests for webhook delivery statuses."""

import pytest
from app.models.webhook_delivery import DeliveryStatus

ALL_STATUSES = sorted([s.value for s in DeliveryStatus])

@pytest.mark.parametrize("status", ALL_STATUSES)
def test_delivery_status_string(status):
    assert isinstance(status, str)

@pytest.mark.parametrize("status", ALL_STATUSES)
def test_delivery_status_in_enum(status):
    assert DeliveryStatus(status) is not None

def test_delivery_has_pending():
    assert "pending" in ALL_STATUSES

def test_delivery_has_delivered():
    assert "delivered" in ALL_STATUSES

def test_delivery_has_failed():
    assert "failed" in ALL_STATUSES

def test_delivery_has_retrying():
    assert "retrying" in ALL_STATUSES

def test_delivery_count():
    assert len(DeliveryStatus) == 4
