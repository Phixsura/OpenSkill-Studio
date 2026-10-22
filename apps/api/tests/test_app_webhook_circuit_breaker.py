"""Webhook circuit breaker tests."""
from app.services.app_webhook_circuit_breaker import (
    record_failure, record_success, is_circuit_open,
    get_circuit_status, reset_circuit, FAILURE_THRESHOLD,
)

EP = "https://test-cb.example.com/hook"

def setup_function():
    reset_circuit(EP)

def test_initially_closed():
    assert is_circuit_open(EP) is False
    assert get_circuit_status(EP) == "closed"

def test_opens_after_threshold():
    for _ in range(FAILURE_THRESHOLD):
        record_failure(EP)
    assert is_circuit_open(EP) is True
    assert get_circuit_status(EP) == "open"

def test_success_resets():
    for _ in range(FAILURE_THRESHOLD):
        record_failure(EP)
    record_success(EP)
    assert is_circuit_open(EP) is False

def test_below_threshold_stays_closed():
    for _ in range(FAILURE_THRESHOLD - 1):
        record_failure(EP)
    assert is_circuit_open(EP) is False

def test_reset():
    for _ in range(FAILURE_THRESHOLD):
        record_failure(EP)
    reset_circuit(EP)
    assert is_circuit_open(EP) is False
