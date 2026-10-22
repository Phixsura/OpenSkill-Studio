"""Webhook retry logic — exponential backoff with jitter.

Determines retry delays and whether a delivery should be retried
based on HTTP status code and attempt count.
"""

import random
import structlog

log = structlog.get_logger()

MAX_ATTEMPTS = 5
BASE_DELAY_SECONDS = 10
MAX_DELAY_SECONDS = 3600  # 1 hour

# HTTP status codes that should trigger a retry
RETRYABLE_STATUS_CODES = frozenset({408, 429, 500, 502, 503, 504})

# Status codes that should NOT be retried (client errors)
NON_RETRYABLE_STATUS_CODES = frozenset({400, 401, 403, 404, 405, 410, 422})


def should_retry(*, http_status: int | None, attempt: int, max_attempts: int = MAX_ATTEMPTS) -> bool:
    """Determine if a webhook delivery should be retried."""
    if attempt >= max_attempts:
        return False

    if http_status is None:
        return True  # Network error — always retry

    if http_status in NON_RETRYABLE_STATUS_CODES:
        return False

    if http_status in RETRYABLE_STATUS_CODES:
        return True

    # 2xx = success, don't retry
    if 200 <= http_status < 300:
        return False

    # Other 4xx = don't retry
    if 400 <= http_status < 500:
        return False

    # Other 5xx = retry
    return http_status >= 500


def get_retry_delay(attempt: int) -> float:
    """Calculate retry delay with exponential backoff + jitter.

    Delay = min(base * 2^attempt + jitter, max_delay)
    """
    delay = min(BASE_DELAY_SECONDS * (2 ** attempt), MAX_DELAY_SECONDS)
    jitter = random.uniform(0, delay * 0.1)  # noqa: S311
    return delay + jitter


def get_retry_schedule(max_attempts: int = MAX_ATTEMPTS) -> list[float]:
    """Get the full retry schedule (delays for each attempt)."""
    return [get_retry_delay(i) for i in range(max_attempts)]
