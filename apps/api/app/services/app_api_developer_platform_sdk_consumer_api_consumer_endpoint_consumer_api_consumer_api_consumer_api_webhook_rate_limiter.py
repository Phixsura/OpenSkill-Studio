"""Consumer API Webhook Rate Limiter — rate limit outgoing webhook deliveries."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timedelta
import structlog

log = structlog.get_logger()

@dataclass
class WebhookRateLimitConfig:
    webhook_id: str
    consumer_id: str
    max_per_second: int = 10
    max_per_minute: int = 100
    max_per_hour: int = 1000
    burst_size: int = 0

@dataclass
class RateLimitResult:
    allowed: bool
    webhook_id: str
    current_second: int
    current_minute: int
    limit_second: int
    limit_minute: int
    retry_after_ms: int = 0

class AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointConsumerApiConsumerApiConsumerApiWebhookRateLimiter:
    def __init__(self) -> None:
        self._configs: dict[tuple[str, str, str], WebhookRateLimitConfig] = {}
        self._sec_counters: dict[tuple[str, str, str, str], int] = {}
        self._min_counters: dict[tuple[str, str, str, str], int] = {}

    def configure(self, installation_id: str, config: WebhookRateLimitConfig) -> WebhookRateLimitConfig:
        if not installation_id:
            raise ValueError("installation_id is required")
        if config.max_per_second < 1:
            raise ValueError("max_per_second must be positive")
        self._configs[(installation_id, config.consumer_id, config.webhook_id)] = config
        return config

    def check_and_consume(self, installation_id: str, consumer_id: str, webhook_id: str, now: datetime) -> RateLimitResult:
        key = (installation_id, consumer_id, webhook_id)
        config = self._configs.get(key, WebhookRateLimitConfig(webhook_id=webhook_id, consumer_id=consumer_id))
        sec_key = (*key, now.strftime("%H%M%S"))
        min_key = (*key, now.strftime("%H%M"))
        sec_count = self._sec_counters.get(sec_key, 0)
        min_count = self._min_counters.get(min_key, 0)
        effective_rps = config.max_per_second + config.burst_size
        if sec_count >= effective_rps:
            return RateLimitResult(allowed=False, webhook_id=webhook_id, current_second=sec_count, current_minute=min_count, limit_second=effective_rps, limit_minute=config.max_per_minute, retry_after_ms=1000)
        if min_count >= config.max_per_minute:
            return RateLimitResult(allowed=False, webhook_id=webhook_id, current_second=sec_count, current_minute=min_count, limit_second=effective_rps, limit_minute=config.max_per_minute, retry_after_ms=60000)
        self._sec_counters[sec_key] = sec_count + 1
        self._min_counters[min_key] = min_count + 1
        return RateLimitResult(allowed=True, webhook_id=webhook_id, current_second=sec_count + 1, current_minute=min_count + 1, limit_second=effective_rps, limit_minute=config.max_per_minute)

    def get_config(self, installation_id: str, consumer_id: str, webhook_id: str) -> WebhookRateLimitConfig | None:
        return self._configs.get((installation_id, consumer_id, webhook_id))

    def list_configs(self, installation_id: str, consumer_id: str) -> list[WebhookRateLimitConfig]:
        return [c for (inst, cid, _), c in self._configs.items() if inst == installation_id and cid == consumer_id]
