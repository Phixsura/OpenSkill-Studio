"""Request timeout manager — dynamic timeout management per endpoint."""
from __future__ import annotations


class TimeoutManager:
    def __init__(self, default_ms: int = 5000):
        self._default = default_ms
        self._overrides: dict[str, int] = {}
        self._timeouts_hit = 0

    def set_timeout(self, endpoint: str, timeout_ms: int) -> dict:
        self._overrides[endpoint] = timeout_ms
        return {"endpoint": endpoint, "timeout_ms": timeout_ms}

    def get_timeout(self, endpoint: str) -> int:
        return self._overrides.get(endpoint, self._default)

    def record_timeout(self, endpoint: str) -> dict:
        self._timeouts_hit += 1
        return {"endpoint": endpoint, "timeouts_total": self._timeouts_hit}

    def stats(self) -> dict:
        return {"default_ms": self._default, "overrides": len(self._overrides),
                "timeouts_hit": self._timeouts_hit}
