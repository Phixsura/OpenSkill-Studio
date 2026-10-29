"""App API Developer Token Usage Monitor — monitor per-token API usage in real-time."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class TokenUsage:
    token_prefix: str
    consumer_id: str
    requests_today: int = 0
    requests_total: int = 0
    last_used_at: float = 0.0
    endpoints_accessed: set[str] = field(default_factory=set)
    error_count: int = 0

    @property
    def error_rate(self) -> float:
        return round(self.error_count / self.requests_total * 100, 1) if self.requests_total > 0 else 0.0

class AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiDeveloperApiTokenUsageMonitor:
    def __init__(self) -> None:
        self._usage: dict[tuple[str, str], TokenUsage] = {}

    def track(self, installation_id: str, token_prefix: str, consumer_id: str, endpoint: str, success: bool = True) -> TokenUsage:
        if not installation_id: raise ValueError("installation_id is required")
        if len(token_prefix) > 12: token_prefix = token_prefix[:12]
        key = (installation_id, token_prefix)
        if key not in self._usage:
            self._usage[key] = TokenUsage(token_prefix=token_prefix, consumer_id=consumer_id)
        u = self._usage[key]
        u.requests_today += 1
        u.requests_total += 1
        u.last_used_at = time.time()
        u.endpoints_accessed.add(endpoint)
        if not success: u.error_count += 1
        return u

    def get(self, installation_id: str, token_prefix: str) -> TokenUsage | None:
        return self._usage.get((installation_id, token_prefix))

    def most_active(self, installation_id: str, limit: int = 10) -> list[TokenUsage]:
        tokens = [u for (inst, _), u in self._usage.items() if inst == installation_id]
        return sorted(tokens, key=lambda u: u.requests_total, reverse=True)[:limit]

    def high_error_tokens(self, installation_id: str, threshold: float = 5.0) -> list[TokenUsage]:
        return [u for (inst, _), u in self._usage.items() if inst == installation_id and u.error_rate >= threshold]

    def all_tokens(self, installation_id: str) -> list[TokenUsage]:
        return [u for (inst, _), u in self._usage.items() if inst == installation_id]
