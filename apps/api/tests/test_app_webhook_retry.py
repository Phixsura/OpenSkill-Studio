"""Webhook retry logic tests."""

import pytest
from app.services.app_webhook_retry import (
    should_retry, get_retry_delay, get_retry_schedule,
    MAX_ATTEMPTS, RETRYABLE_STATUS_CODES, NON_RETRYABLE_STATUS_CODES,
)

@pytest.mark.parametrize("status", sorted(RETRYABLE_STATUS_CODES))
def test_retryable_status(status):
    assert should_retry(http_status=status, attempt=0) is True

@pytest.mark.parametrize("status", sorted(NON_RETRYABLE_STATUS_CODES))
def test_non_retryable_status(status):
    assert should_retry(http_status=status, attempt=0) is False

SUCCESS_CODES = [200, 201, 204]
@pytest.mark.parametrize("status", SUCCESS_CODES)
def test_success_no_retry(status):
    assert should_retry(http_status=status, attempt=0) is False

def test_network_error_retries():
    assert should_retry(http_status=None, attempt=0) is True

def test_max_attempts_exceeded():
    assert should_retry(http_status=500, attempt=MAX_ATTEMPTS) is False

def test_last_attempt_ok():
    assert should_retry(http_status=500, attempt=MAX_ATTEMPTS - 1) is True

def test_delay_increases():
    d0 = get_retry_delay(0)
    d1 = get_retry_delay(1)
    d2 = get_retry_delay(2)
    assert d1 > d0
    assert d2 > d1

def test_delay_bounded():
    d = get_retry_delay(100)
    assert d <= 3700  # max + 10% jitter

def test_delay_positive():
    for i in range(10):
        assert get_retry_delay(i) > 0

def test_schedule_length():
    schedule = get_retry_schedule()
    assert len(schedule) == MAX_ATTEMPTS

def test_schedule_increasing():
    schedule = get_retry_schedule()
    for i in range(1, len(schedule)):
        assert schedule[i] >= schedule[i - 1] * 0.9  # allow jitter variance
