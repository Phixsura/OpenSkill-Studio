"""App API Webhook Timeout — manage delivery timeout settings.

Manages webhook timeouts:
- Configure timeouts per destination
- Track timeout occurrences
- Default and per-destination overrides
- Per-installation scoped configs
"""

from __future__ import annotations

from dataclasses import dataclass

import structlog

log = structlog.get_logger()


@dataclass
class TimeoutConfig:
    """Timeout configuration for a destination."""

    destination: str
    connect_timeout_ms: int = 5000
    read_timeout_ms: int = 30000
    timeout_count: int = 0


class AppAPIWebhookTimeout:
    """Manage delivery timeout settings."""

    def __init__(self, default_connect: int = 5000, default_read: int = 30000) -> None:
        self._default_connect = default_connect
        self._default_read = default_read
        self._configs: dict[tuple[str, str], TimeoutConfig] = {}

    def configure(
        self, installation_id: str, destination: str,
        connect_timeout_ms: int = 5000, read_timeout_ms: int = 30000,
    ) -> TimeoutConfig:
        if not installation_id:
            raise ValueError("installation_id is required")
        if connect_timeout_ms < 100:
            raise ValueError("connect_timeout_ms must be at least 100")
        if read_timeout_ms < 100:
            raise ValueError("read_timeout_ms must be at least 100")

        config = TimeoutConfig(
            destination=destination,
            connect_timeout_ms=connect_timeout_ms,
            read_timeout_ms=read_timeout_ms,
        )
        self._configs[(installation_id, destination)] = config
        return config

    def get_timeout(self, installation_id: str, destination: str) -> TimeoutConfig:
        config = self._configs.get((installation_id, destination))
        if config is None:
            return TimeoutConfig(
                destination=destination,
                connect_timeout_ms=self._default_connect,
                read_timeout_ms=self._default_read,
            )
        return config

    def record_timeout(self, installation_id: str, destination: str) -> TimeoutConfig:
        config = self.get_timeout(installation_id, destination)
        config.timeout_count += 1
        self._configs[(installation_id, destination)] = config
        return config

    def frequent_timeouts(self, installation_id: str, threshold: int = 5) -> list[TimeoutConfig]:
        return [c for (inst, _), c in self._configs.items() if inst == installation_id and c.timeout_count >= threshold]

    def list_configs(self, installation_id: str) -> list[TimeoutConfig]:
        return [c for (inst, _), c in self._configs.items() if inst == installation_id]
