"""Rate Limit Dashboard — monitor and configure API rate limits per client."""
from __future__ import annotations
from dataclasses import dataclass, field
import time


@dataclass
class RateLimitBucket:
    client_id: str
    endpoint: str
    max_requests: int
    window_seconds: int
    requests: list[float] = field(default_factory=list)

    def is_limited(self) -> bool:
        now = time.time()
        cutoff = now - self.window_seconds
        self.requests = [t for t in self.requests if t > cutoff]
        return len(self.requests) >= self.max_requests

    def record(self) -> bool:
        if self.is_limited():
            return False
        self.requests.append(time.time())
        return True

    @property
    def remaining(self) -> int:
        now = time.time()
        cutoff = now - self.window_seconds
        active = sum(1 for t in self.requests if t > cutoff)
        return max(0, self.max_requests - active)


class RateLimitDashboardService:
    def __init__(self):
        self._buckets: dict[str, RateLimitBucket] = {}
        self._defaults: dict[str, tuple[int, int]] = {
            "GET": (100, 60), "POST": (30, 60), "DELETE": (10, 60),
        }

    def _key(self, client_id: str, endpoint: str) -> str:
        return f"{client_id}:{endpoint}"

    def configure(self, client_id: str, endpoint: str, max_req: int,
                  window: int) -> RateLimitBucket:
        key = self._key(client_id, endpoint)
        bucket = RateLimitBucket(client_id=client_id, endpoint=endpoint,
                                 max_requests=max_req, window_seconds=window)
        self._buckets[key] = bucket
        return bucket

    def check_and_record(self, client_id: str, endpoint: str,
                         method: str = "GET") -> tuple[bool, int]:
        key = self._key(client_id, endpoint)
        bucket = self._buckets.get(key)
        if not bucket:
            defaults = self._defaults.get(method, (100, 60))
            bucket = self.configure(client_id, endpoint, defaults[0], defaults[1])
        allowed = bucket.record()
        return allowed, bucket.remaining

    def get_dashboard(self, client_id: str) -> list[dict]:
        return [{"endpoint": b.endpoint, "max": b.max_requests,
                 "remaining": b.remaining, "window": b.window_seconds}
                for b in self._buckets.values() if b.client_id == client_id]
