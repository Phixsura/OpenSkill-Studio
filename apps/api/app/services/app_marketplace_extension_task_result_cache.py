"""Task Result Cache — cache expensive computation results with staleness control.

For long-running tasks (reports, aggregations), cache the result and
serve it while recomputation happens in the background.

Implements:
- Cache task results by task key + params hash
- Stale-while-recompute (serve old result while new one computes)
- Computation lock (prevent duplicate concurrent computations)
- Result versioning (track generations)
- TTL with soft/hard expiry
"""
from __future__ import annotations
from dataclasses import dataclass, field
import hashlib
import json
import time


@dataclass
class TaskResult:
    task_key: str
    params_hash: str
    result: object
    version: int
    computed_at: float
    soft_ttl: float  # serve stale after this
    hard_ttl: float  # discard after this
    computing: bool = False
    compute_count: int = 0

    @property
    def is_fresh(self) -> bool:
        return time.time() < self.computed_at + self.soft_ttl

    @property
    def is_expired(self) -> bool:
        return time.time() > self.computed_at + self.hard_ttl

    @property
    def is_stale(self) -> bool:
        return not self.is_fresh and not self.is_expired


class TaskResultCacheService:
    def __init__(self):
        self._cache: dict[str, TaskResult] = {}
        self._version_counter = 0

    def _cache_key(self, task_key: str, params: dict) -> str:
        params_hash = hashlib.md5(
            json.dumps(params, sort_keys=True, default=str).encode()
        ).hexdigest()[:12]
        return f"{task_key}:{params_hash}"

    def get(self, task_key: str, params: dict) -> dict:
        """Get cached result. Returns status + result if available."""
        key = self._cache_key(task_key, params)
        cached = self._cache.get(key)

        if not cached:
            return {"status": "miss", "result": None}

        if cached.is_expired:
            del self._cache[key]
            return {"status": "expired", "result": None}

        if cached.is_fresh:
            return {"status": "fresh", "result": cached.result,
                    "version": cached.version,
                    "age_seconds": round(time.time() - cached.computed_at, 1)}

        # Stale but servable
        return {"status": "stale", "result": cached.result,
                "version": cached.version,
                "needs_recompute": True,
                "age_seconds": round(time.time() - cached.computed_at, 1)}

    def try_lock(self, task_key: str, params: dict) -> bool:
        """Try to acquire computation lock. Prevents duplicate work."""
        key = self._cache_key(task_key, params)
        cached = self._cache.get(key)
        if cached and cached.computing:
            return False  # someone else is computing
        if not cached:
            self._version_counter += 1
            cached = TaskResult(task_key=task_key,
                                params_hash=key.split(":")[-1],
                                result=None, version=self._version_counter,
                                computed_at=0, soft_ttl=0, hard_ttl=0,
                                computing=True)
            self._cache[key] = cached
        else:
            cached.computing = True
        return True

    def store(self, task_key: str, params: dict, result: object,
              soft_ttl: float = 300, hard_ttl: float = 3600) -> TaskResult:
        """Store computation result. Releases lock."""
        key = self._cache_key(task_key, params)
        self._version_counter += 1
        cached = TaskResult(
            task_key=task_key,
            params_hash=key.split(":")[-1],
            result=result,
            version=self._version_counter,
            computed_at=time.time(),
            soft_ttl=soft_ttl,
            hard_ttl=hard_ttl,
            computing=False)
        existing = self._cache.get(key)
        if existing:
            cached.compute_count = existing.compute_count + 1
        else:
            cached.compute_count = 1
        self._cache[key] = cached
        return cached

    def invalidate(self, task_key: str, params: dict) -> bool:
        key = self._cache_key(task_key, params)
        return self._cache.pop(key, None) is not None

    def get_or_compute(self, task_key: str, params: dict,
                       compute_fn: callable,
                       soft_ttl: float = 300,
                       hard_ttl: float = 3600) -> dict:
        """Get from cache or compute. Stale = serve + recompute."""
        result = self.get(task_key, params)

        if result["status"] == "fresh":
            return result

        if result["status"] == "stale":
            # Serve stale, trigger recompute if not locked
            if self.try_lock(task_key, params):
                new_result = compute_fn(params)
                self.store(task_key, params, new_result, soft_ttl, hard_ttl)
            return result  # serve stale immediately

        # Miss or expired — compute synchronously
        if self.try_lock(task_key, params):
            new_result = compute_fn(params)
            cached = self.store(task_key, params, new_result, soft_ttl, hard_ttl)
            return {"status": "computed", "result": new_result,
                    "version": cached.version}
        return {"status": "computing", "result": None}

    def stats(self) -> dict:
        now = time.time()
        fresh = sum(1 for c in self._cache.values() if c.is_fresh)
        stale = sum(1 for c in self._cache.values() if c.is_stale)
        computing = sum(1 for c in self._cache.values() if c.computing)
        return {"total": len(self._cache), "fresh": fresh,
                "stale": stale, "computing": computing}
