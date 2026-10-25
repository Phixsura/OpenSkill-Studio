"""Canary Deploy — progressive rollout of extension updates.

Implements canary deployment: gradually increase traffic to a new version
while monitoring error rates, with automatic rollback on failure.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class CanaryState(str, Enum):
    PENDING = "pending"
    ROLLING_OUT = "rolling_out"
    PAUSED = "paused"
    PROMOTED = "promoted"
    ROLLED_BACK = "rolled_back"


@dataclass
class CanaryDeployment:
    deploy_id: str
    extension_id: str
    stable_version: str
    canary_version: str
    state: CanaryState = CanaryState.PENDING
    canary_percent: int = 0
    target_percent: int = 100
    step_percent: int = 10
    error_threshold: float = 5.0
    canary_errors: int = 0
    canary_requests: int = 0
    stable_errors: int = 0
    stable_requests: int = 0
    created_at: str = ""
    steps_log: list[dict] = field(default_factory=list)

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()

    @property
    def canary_error_rate(self) -> float:
        if self.canary_requests == 0:
            return 0.0
        return round(self.canary_errors / self.canary_requests * 100, 2)


class CanaryDeployService:
    """Manages progressive canary rollouts for extensions."""

    def __init__(self):
        self._deploys: dict[str, CanaryDeployment] = {}

    def create(self, deploy_id: str, extension_id: str, stable: str, canary: str,
               step_percent: int = 10, error_threshold: float = 5.0) -> CanaryDeployment:
        deploy = CanaryDeployment(
            deploy_id=deploy_id, extension_id=extension_id,
            stable_version=stable, canary_version=canary,
            step_percent=step_percent, error_threshold=error_threshold,
        )
        self._deploys[deploy_id] = deploy
        return deploy

    def start(self, deploy_id: str) -> bool:
        d = self._deploys.get(deploy_id)
        if d and d.state == CanaryState.PENDING:
            d.state = CanaryState.ROLLING_OUT
            d.canary_percent = d.step_percent
            d.steps_log.append({"action": "start", "percent": d.canary_percent})
            return True
        return False

    def advance(self, deploy_id: str) -> tuple[bool, str]:
        """Advance canary to next step if error rate is acceptable."""
        d = self._deploys.get(deploy_id)
        if not d or d.state != CanaryState.ROLLING_OUT:
            return False, "Not in rolling out state"

        if d.canary_error_rate > d.error_threshold:
            d.state = CanaryState.ROLLED_BACK
            d.steps_log.append({"action": "auto_rollback", "error_rate": d.canary_error_rate})
            return False, f"Auto-rollback: error rate {d.canary_error_rate}% > {d.error_threshold}%"

        d.canary_percent = min(d.target_percent, d.canary_percent + d.step_percent)
        d.steps_log.append({"action": "advance", "percent": d.canary_percent})

        if d.canary_percent >= d.target_percent:
            d.state = CanaryState.PROMOTED
            d.steps_log.append({"action": "promoted"})

        return True, f"Canary at {d.canary_percent}%"

    def record_request(self, deploy_id: str, is_canary: bool, is_error: bool) -> None:
        d = self._deploys.get(deploy_id)
        if not d:
            return
        if is_canary:
            d.canary_requests += 1
            if is_error:
                d.canary_errors += 1
        else:
            d.stable_requests += 1
            if is_error:
                d.stable_errors += 1

    def rollback(self, deploy_id: str, reason: str = "") -> bool:
        d = self._deploys.get(deploy_id)
        if d and d.state in (CanaryState.ROLLING_OUT, CanaryState.PAUSED):
            d.state = CanaryState.ROLLED_BACK
            d.canary_percent = 0
            d.steps_log.append({"action": "manual_rollback", "reason": reason})
            return True
        return False

    def get(self, deploy_id: str) -> CanaryDeployment | None:
        return self._deploys.get(deploy_id)

    def get_routing(self, deploy_id: str) -> dict:
        """Get traffic routing split."""
        d = self._deploys.get(deploy_id)
        if not d:
            return {}
        return {
            "canary_version": d.canary_version, "canary_percent": d.canary_percent,
            "stable_version": d.stable_version, "stable_percent": 100 - d.canary_percent,
        }
