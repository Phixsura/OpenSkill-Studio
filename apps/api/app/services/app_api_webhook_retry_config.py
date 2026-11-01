"""App API Webhook Retry Config — configure retry behavior per destination.

Manages retry configurations:
- Define retry strategy (fixed/exponential)
- Max attempts and delay settings
- Per-destination overrides
- Per-installation scoped configs
"""

from __future__ import annotations

from dataclasses import dataclass

import structlog

log = structlog.get_logger()


@dataclass
class RetryConfig:
    """Retry configuration for a destination."""

    config_id: str
    destination: str
    strategy: str  # "fixed", "exponential"
    max_attempts: int = 5
    initial_delay_ms: int = 1000
    max_delay_ms: int = 60000

    def delay_for_attempt(self, attempt: int) -> int:
        """Calculate delay in ms for given attempt (1-based)."""
        if attempt < 1:
            return 0
        if self.strategy == "fixed":
            return self.initial_delay_ms
        # exponential: initial * 2^(attempt-1), capped at max
        delay = self.initial_delay_ms * (2 ** (attempt - 1))
        return min(delay, self.max_delay_ms)


class AppAPIWebhookRetryConfig:
    """Configure retry behavior per destination."""

    def __init__(self) -> None:
        self._configs: dict[tuple[str, str], RetryConfig] = {}

    def set_config(
        self, installation_id: str, config_id: str, destination: str,
        strategy: str = "exponential", max_attempts: int = 5,
        initial_delay_ms: int = 1000, max_delay_ms: int = 60000,
    ) -> RetryConfig:
        if not installation_id:
            raise ValueError("installation_id is required")
        if strategy not in ("fixed", "exponential"):
            raise ValueError("strategy must be fixed or exponential")
        if max_attempts < 1:
            raise ValueError("max_attempts must be at least 1")

        config = RetryConfig(
            config_id=config_id, destination=destination,
            strategy=strategy, max_attempts=max_attempts,
            initial_delay_ms=initial_delay_ms, max_delay_ms=max_delay_ms,
        )
        self._configs[(installation_id, config_id)] = config
        return config

    def get_for_destination(self, installation_id: str, destination: str) -> RetryConfig | None:
        for (inst, _), c in self._configs.items():
            if inst == installation_id and c.destination == destination:
                return c
        return None

    def list_configs(self, installation_id: str) -> list[RetryConfig]:
        return [c for (inst, _), c in self._configs.items() if inst == installation_id]
