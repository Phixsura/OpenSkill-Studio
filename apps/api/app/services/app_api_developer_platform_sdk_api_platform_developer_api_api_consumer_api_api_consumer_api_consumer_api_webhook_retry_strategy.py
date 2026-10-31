"""Consumer API Webhook Retry Strategy — configurable retry strategies per webhook."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import structlog

log = structlog.get_logger()

@dataclass
class RetryStrategy:
    strategy_id: str
    webhook_id: str
    max_retries: int = 5
    strategy_type: str = "exponential"  # "exponential", "linear", "fixed"
    base_delay_seconds: int = 10
    max_delay_seconds: int = 3600
    multiplier: float = 2.0
    jitter: bool = True

@dataclass
class RetrySchedule:
    attempt: int
    delay_seconds: int
    scheduled_at: datetime

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiWebhookRetryStrategy:
    def __init__(self) -> None:
        self._strategies: dict[tuple[str, str, str], RetryStrategy] = {}

    def set_strategy(self, installation_id: str, consumer_id: str, strategy: RetryStrategy) -> RetryStrategy:
        if not installation_id:
            raise ValueError("installation_id is required")
        if strategy.strategy_type not in ("exponential", "linear", "fixed"):
            raise ValueError(f"Invalid strategy_type: {strategy.strategy_type}")
        if strategy.max_retries < 0:
            raise ValueError("max_retries must be non-negative")
        if strategy.base_delay_seconds < 1:
            raise ValueError("base_delay_seconds must be positive")
        self._strategies[(installation_id, consumer_id, strategy.webhook_id)] = strategy
        return strategy

    def compute_delay(self, installation_id: str, consumer_id: str, webhook_id: str, attempt: int) -> int:
        key = (installation_id, consumer_id, webhook_id)
        strategy = self._strategies.get(key, RetryStrategy(strategy_id="default", webhook_id=webhook_id))
        if attempt > strategy.max_retries:
            return -1  # give up
        if strategy.strategy_type == "exponential":
            delay = int(strategy.base_delay_seconds * (strategy.multiplier ** (attempt - 1)))
        elif strategy.strategy_type == "linear":
            delay = strategy.base_delay_seconds * attempt
        else:  # fixed
            delay = strategy.base_delay_seconds
        return min(delay, strategy.max_delay_seconds)

    def get_schedule(self, installation_id: str, consumer_id: str, webhook_id: str, failed_at: datetime) -> list[RetrySchedule]:
        key = (installation_id, consumer_id, webhook_id)
        strategy = self._strategies.get(key, RetryStrategy(strategy_id="default", webhook_id=webhook_id))
        schedule: list[RetrySchedule] = []
        current = failed_at
        for attempt in range(1, strategy.max_retries + 1):
            delay = self.compute_delay(installation_id, consumer_id, webhook_id, attempt)
            if delay < 0:
                break
            current = current + timedelta(seconds=delay)
            schedule.append(RetrySchedule(attempt=attempt, delay_seconds=delay, scheduled_at=current))
        return schedule

    def get_strategy(self, installation_id: str, consumer_id: str, webhook_id: str) -> RetryStrategy | None:
        return self._strategies.get((installation_id, consumer_id, webhook_id))
