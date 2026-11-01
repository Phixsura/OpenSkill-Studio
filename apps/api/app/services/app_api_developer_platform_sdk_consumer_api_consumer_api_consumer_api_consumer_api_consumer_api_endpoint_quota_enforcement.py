"""Consumer API Endpoint Quota Enforcement — enforce per-endpoint request quotas."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timedelta
import structlog

log = structlog.get_logger()

@dataclass
class EndpointQuota:
    endpoint_path: str
    consumer_id: str
    max_requests: int
    window_seconds: int = 3600  # 1 hour default
    current_count: int = 0
    window_start: datetime | None = None

@dataclass
class QuotaEnforceResult:
    allowed: bool
    endpoint: str
    current: int
    limit: int
    remaining: int
    reset_at: datetime | None = None
    retry_after_seconds: int = 0

class AppAPIDeveloperPlatformSDKConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiEndpointQuotaEnforcement:
    def __init__(self) -> None:
        self._quotas: dict[tuple[str, str, str], EndpointQuota] = {}

    def set_quota(self, installation_id: str, quota: EndpointQuota) -> EndpointQuota:
        if not installation_id:
            raise ValueError("installation_id is required")
        if quota.max_requests < 1:
            raise ValueError("max_requests must be positive")
        if quota.window_seconds < 1:
            raise ValueError("window_seconds must be positive")
        self._quotas[(installation_id, quota.consumer_id, quota.endpoint_path)] = quota
        return quota

    def check_and_consume(self, installation_id: str, consumer_id: str, endpoint_path: str, now: datetime) -> QuotaEnforceResult:
        key = (installation_id, consumer_id, endpoint_path)
        quota = self._quotas.get(key)
        if not quota:
            return QuotaEnforceResult(allowed=True, endpoint=endpoint_path, current=0, limit=0, remaining=0)
        # Reset window if expired
        if quota.window_start is None or now >= quota.window_start + timedelta(seconds=quota.window_seconds):
            quota.window_start = now
            quota.current_count = 0
        reset_at = quota.window_start + timedelta(seconds=quota.window_seconds)
        if quota.current_count >= quota.max_requests:
            retry_after = int((reset_at - now).total_seconds())
            return QuotaEnforceResult(allowed=False, endpoint=endpoint_path, current=quota.current_count, limit=quota.max_requests, remaining=0, reset_at=reset_at, retry_after_seconds=max(0, retry_after))
        quota.current_count += 1
        remaining = quota.max_requests - quota.current_count
        return QuotaEnforceResult(allowed=True, endpoint=endpoint_path, current=quota.current_count, limit=quota.max_requests, remaining=remaining, reset_at=reset_at)

    def get_status(self, installation_id: str, consumer_id: str, endpoint_path: str, now: datetime) -> QuotaEnforceResult:
        key = (installation_id, consumer_id, endpoint_path)
        quota = self._quotas.get(key)
        if not quota:
            return QuotaEnforceResult(allowed=True, endpoint=endpoint_path, current=0, limit=0, remaining=0)
        if quota.window_start and now >= quota.window_start + timedelta(seconds=quota.window_seconds):
            return QuotaEnforceResult(allowed=True, endpoint=endpoint_path, current=0, limit=quota.max_requests, remaining=quota.max_requests)
        remaining = max(0, quota.max_requests - quota.current_count)
        return QuotaEnforceResult(allowed=remaining > 0, endpoint=endpoint_path, current=quota.current_count, limit=quota.max_requests, remaining=remaining)
