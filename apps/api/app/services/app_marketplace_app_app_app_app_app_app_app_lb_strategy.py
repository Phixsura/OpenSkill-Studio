"""Load balancer strategy engine — multiple LB algorithms."""
from __future__ import annotations
import hashlib


class LoadBalancer:
    def __init__(self, backends: list[str], strategy: str = "round_robin"):
        self._backends = backends
        self._strategy = strategy
        self._idx = 0
        self._weights: dict[str, int] = {b: 1 for b in backends}

    def set_weight(self, backend: str, weight: int) -> None:
        self._weights[backend] = weight

    def next(self, key: str = "") -> dict:
        if self._strategy == "round_robin":
            backend = self._backends[self._idx % len(self._backends)]
            self._idx += 1
        elif self._strategy == "hash":
            h = int(hashlib.md5(key.encode()).hexdigest(), 16)
            backend = self._backends[h % len(self._backends)]
        elif self._strategy == "weighted":
            total = sum(self._weights[b] for b in self._backends)
            pick = self._idx % total
            cumulative = 0
            backend = self._backends[0]
            for b in self._backends:
                cumulative += self._weights[b]
                if pick < cumulative:
                    backend = b
                    break
            self._idx += 1
        else:
            backend = self._backends[0]
        return {"backend": backend, "strategy": self._strategy}

    def stats(self) -> dict:
        return {"backends": len(self._backends), "strategy": self._strategy,
                "weights": dict(self._weights)}
