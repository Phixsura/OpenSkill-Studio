"""Extension Canary Deploy — gradual rollout of new extension versions."""
from __future__ import annotations
from dataclasses import dataclass
import hashlib
import time


@dataclass
class CanaryDeploy:
    deploy_id: str
    extension_id: str
    stable_version: str
    canary_version: str
    rollout_pct: int = 5  # 0-100
    status: str = "active"  # active, promoting, rolled_back, completed
    error_threshold: float = 5.0  # % error rate to auto-rollback
    errors_canary: int = 0
    requests_canary: int = 0
    created_at: float = 0.0
    def __post_init__(self):
        if not self.created_at: self.created_at = time.time()

    @property
    def error_rate(self) -> float:
        return (self.errors_canary / self.requests_canary * 100) if self.requests_canary > 0 else 0.0


class ExtCanaryDeployService:
    def __init__(self):
        self._deploys: dict[str, CanaryDeploy] = {}
        self._counter = 0

    def create(self, extension_id: str, stable: str, canary: str,
               initial_pct: int = 5, error_threshold: float = 5.0) -> CanaryDeploy:
        self._counter += 1
        d = CanaryDeploy(deploy_id=f"canary-{self._counter}",
                         extension_id=extension_id, stable_version=stable,
                         canary_version=canary, rollout_pct=initial_pct,
                         error_threshold=error_threshold)
        self._deploys[d.deploy_id] = d
        return d

    def route(self, deploy_id: str, user_id: str) -> str:
        d = self._deploys.get(deploy_id)
        if not d or d.status != "active":
            return d.stable_version if d else ""
        h = int(hashlib.md5(f"{deploy_id}:{user_id}".encode()).hexdigest(), 16)
        if (h % 100) < d.rollout_pct:
            d.requests_canary += 1
            return d.canary_version
        return d.stable_version

    def report_error(self, deploy_id: str) -> bool:
        d = self._deploys.get(deploy_id)
        if not d or d.status != "active": return False
        d.errors_canary += 1
        if d.error_rate > d.error_threshold:
            d.status = "rolled_back"
        return True

    def increase_rollout(self, deploy_id: str, pct: int) -> bool:
        d = self._deploys.get(deploy_id)
        if not d or d.status != "active" or pct < d.rollout_pct: return False
        d.rollout_pct = min(100, pct)
        if d.rollout_pct >= 100:
            d.status = "completed"
        return True

    def rollback(self, deploy_id: str) -> bool:
        d = self._deploys.get(deploy_id)
        if not d or d.status != "active": return False
        d.status = "rolled_back"
        return True
