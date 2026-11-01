"""Webhook delivery summary tests."""
import pytest
from app.services.app_webhook_summary import compute_delivery_summary

def test_empty():
    s = compute_delivery_summary([])
    assert s["total"] == 0
    assert s["success_rate"] == 100.0

def test_all_delivered():
    deliveries = [{"status": "delivered", "duration_ms": 100} for _ in range(10)]
    s = compute_delivery_summary(deliveries)
    assert s["success_rate"] == 100.0
    assert s["delivered"] == 10

def test_mixed():
    deliveries = [
        {"status": "delivered", "duration_ms": 100},
        {"status": "delivered", "duration_ms": 200},
        {"status": "failed", "duration_ms": 5000},
        {"status": "retrying"},
    ]
    s = compute_delivery_summary(deliveries)
    assert s["total"] == 4
    assert s["delivered"] == 2
    assert s["failed"] == 1
    assert s["success_rate"] == round(2/3*100, 1)

def test_avg_duration():
    deliveries = [{"status": "delivered", "duration_ms": d} for d in [100, 200, 300]]
    s = compute_delivery_summary(deliveries)
    assert s["avg_duration_ms"] == 200.0
