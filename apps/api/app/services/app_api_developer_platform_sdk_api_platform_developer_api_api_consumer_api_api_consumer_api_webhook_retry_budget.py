"""Webhook Retry Budget — limit total retries per consumer per time window."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
import structlog

log = structlog.get_logger()

@dataclass
class RetryBudgetConfig:
    consumer_id: str
    max_retries_per_hour: int = 100
    max_retries_per_day: int = 1000
    cooldown_minutes: int = 5  # pause after budget exhaustion

@dataclass
class RetryRecord:
    webhook_id: str
    attempt: int
    timestamp: datetime
    success: bool

@dataclass
class BudgetStatus:
    hourly_used: int
    hourly_limit: int
    daily_used: int
    daily_limit: int
    exhausted: bool
    cooldown_until: datetime | None = None

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiWebhookRetryBudget:
    def __init__(self) -> None:
        self._configs: dict[tuple[str, str], RetryBudgetConfig] = {}
        self._records: dict[tuple[str, str], list[RetryRecord]] = {}

    def set_config(self, installation_id: str, config: RetryBudgetConfig) -> RetryBudgetConfig:
        if not installation_id:
            raise ValueError("installation_id is required")
        if config.max_retries_per_hour < 1:
            raise ValueError("max_retries_per_hour must be positive")
        self._configs[(installation_id, config.consumer_id)] = config
        return config

    def record_retry(self, installation_id: str, consumer_id: str, record: RetryRecord) -> RetryRecord:
        key = (installation_id, consumer_id)
        if key not in self._records:
            self._records[key] = []
        self._records[key].append(record)
        return record

    def check_budget(self, installation_id: str, consumer_id: str, now: datetime) -> BudgetStatus:
        from datetime import timedelta
        key = (installation_id, consumer_id)
        config = self._configs.get(key, RetryBudgetConfig(consumer_id=consumer_id))
        records = self._records.get(key, [])
        hour_ago = now - timedelta(hours=1)
        day_ago = now - timedelta(days=1)
        hourly = sum(1 for r in records if r.timestamp >= hour_ago)
        daily = sum(1 for r in records if r.timestamp >= day_ago)
        exhausted = hourly >= config.max_retries_per_hour or daily >= config.max_retries_per_day
        cooldown = now + timedelta(minutes=config.cooldown_minutes) if exhausted else None
        return BudgetStatus(hourly_used=hourly, hourly_limit=config.max_retries_per_hour, daily_used=daily, daily_limit=config.max_retries_per_day, exhausted=exhausted, cooldown_until=cooldown)

    def success_rate(self, installation_id: str, consumer_id: str) -> float:
        records = self._records.get((installation_id, consumer_id), [])
        if not records:
            return 1.0
        return sum(1 for r in records if r.success) / len(records)
