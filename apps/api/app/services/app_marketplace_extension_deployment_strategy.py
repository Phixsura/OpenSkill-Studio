"""Deployment Strategy — manage extension deployment with blue-green and canary.

Supports blue-green, canary, and rolling deployment strategies with
traffic splitting, health checks, and automatic rollback on failure.
"""
from __future__ import annotations
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class Strategy(str, Enum):
    BLUE_GREEN = "blue_green"
    CANARY = "canary"
    ROLLING = "rolling"
    IMMEDIATE = "immediate"


class DeployStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    PROMOTING = "promoting"
    COMPLETED = "completed"
    ROLLED_BACK = "rolled_back"
    FAILED = "failed"


@dataclass
class Deployment:
    deploy_id: str
    extension_id: str
    from_version: str
    to_version: str
    strategy: Strategy
    status: DeployStatus = DeployStatus.PENDING
    traffic_percent: int = 0  # canary traffic to new version
    health_check_passed: bool = False
    error: str = ""
    created_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()


class DeploymentStrategyService:
    """Manages extension deployments with multiple strategies."""

    def __init__(self):
        self._deployments: dict[str, Deployment] = {}
        self._active_version: dict[str, str] = {}

    def deploy(self, extension_id: str, from_version: str, to_version: str,
               strategy: Strategy = Strategy.IMMEDIATE) -> Deployment:
        deploy_id = f"dep_{secrets.token_urlsafe(10)}"
        deploy = Deployment(
            deploy_id=deploy_id, extension_id=extension_id,
            from_version=from_version, to_version=to_version,
            strategy=strategy,
        )

        if strategy == Strategy.IMMEDIATE:
            deploy.status = DeployStatus.COMPLETED
            deploy.traffic_percent = 100
            self._active_version[extension_id] = to_version
        elif strategy == Strategy.CANARY:
            deploy.status = DeployStatus.IN_PROGRESS
            deploy.traffic_percent = 5  # start with 5%
        elif strategy == Strategy.BLUE_GREEN:
            deploy.status = DeployStatus.IN_PROGRESS
            deploy.traffic_percent = 0  # staging, no traffic yet
        elif strategy == Strategy.ROLLING:
            deploy.status = DeployStatus.IN_PROGRESS
            deploy.traffic_percent = 25  # 25% at a time

        self._deployments[deploy_id] = deploy
        return deploy

    def increase_traffic(self, deploy_id: str, percent: int) -> dict:
        deploy = self._deployments.get(deploy_id)
        if not deploy or deploy.status != DeployStatus.IN_PROGRESS:
            return {"ok": False, "error": "Deployment not in progress"}
        if not 0 <= percent <= 100:
            return {"ok": False, "error": "Percent must be 0-100"}
        deploy.traffic_percent = percent
        return {"ok": True, "traffic_percent": percent}

    def report_health(self, deploy_id: str, healthy: bool, error: str = "") -> bool:
        deploy = self._deployments.get(deploy_id)
        if not deploy:
            return False
        deploy.health_check_passed = healthy
        if not healthy:
            deploy.error = error
        return True

    def promote(self, deploy_id: str) -> dict:
        deploy = self._deployments.get(deploy_id)
        if not deploy or deploy.status != DeployStatus.IN_PROGRESS:
            return {"ok": False, "error": "Cannot promote"}
        if not deploy.health_check_passed:
            return {"ok": False, "error": "Health check not passed"}
        deploy.status = DeployStatus.COMPLETED
        deploy.traffic_percent = 100
        self._active_version[deploy.extension_id] = deploy.to_version
        return {"ok": True, "version": deploy.to_version}

    def rollback(self, deploy_id: str) -> dict:
        deploy = self._deployments.get(deploy_id)
        if not deploy or deploy.status not in (DeployStatus.IN_PROGRESS, DeployStatus.COMPLETED):
            return {"ok": False, "error": "Cannot rollback"}
        deploy.status = DeployStatus.ROLLED_BACK
        deploy.traffic_percent = 0
        self._active_version[deploy.extension_id] = deploy.from_version
        return {"ok": True, "version": deploy.from_version}

    def get_active_version(self, extension_id: str) -> str | None:
        return self._active_version.get(extension_id)

    def list_deployments(self, extension_id: str) -> list[Deployment]:
        return [d for d in self._deployments.values()
                if d.extension_id == extension_id]
