"""App Canary Deploy — progressive traffic shifting for releases.

Manages canary deployments:
- Define canary stages with traffic percentages
- Progress through stages with health checks
- Rollback on failure
- Per-installation scoped deployments
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum

import structlog

log = structlog.get_logger()


class DeployStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ROLLED_BACK = "rolled_back"


@dataclass
class CanaryStage:
    """A canary deployment stage."""

    stage_id: str
    traffic_pct: float
    duration_seconds: int
    health_threshold: float = 0.95
    started_at: float | None = None
    healthy: bool | None = None


@dataclass
class CanaryDeploy:
    """A canary deployment."""

    deploy_id: str
    version: str
    stages: list[CanaryStage]
    current_stage: int = 0
    status: DeployStatus = DeployStatus.PENDING
    created_at: float = field(default_factory=time.time)


class AppCanaryDeploy:
    """Manage progressive canary deployments."""

    def __init__(self) -> None:
        self._deploys: dict[tuple[str, str], CanaryDeploy] = {}

    def create_deploy(
        self, installation_id: str, deploy_id: str, version: str,
        stages: list[dict],
    ) -> CanaryDeploy:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not deploy_id:
            raise ValueError("deploy_id is required")
        if not stages:
            raise ValueError("at least one stage is required")

        # Validate traffic percentages are ascending
        pcts = [s["traffic_pct"] for s in stages]
        for p in pcts:
            if not (0 < p <= 100):
                raise ValueError("traffic_pct must be between 0 and 100")
        if pcts != sorted(pcts):
            raise ValueError("stages must have ascending traffic percentages")

        stage_objs = [
            CanaryStage(
                stage_id=s["stage_id"], traffic_pct=s["traffic_pct"],
                duration_seconds=s.get("duration_seconds", 300),
                health_threshold=s.get("health_threshold", 0.95),
            )
            for s in stages
        ]

        deploy = CanaryDeploy(deploy_id=deploy_id, version=version, stages=stage_objs)
        self._deploys[(installation_id, deploy_id)] = deploy
        return deploy

    def start(self, installation_id: str, deploy_id: str) -> CanaryDeploy:
        d = self._get(installation_id, deploy_id)
        if d.status != DeployStatus.PENDING:
            raise ValueError("Deploy already started")
        d.status = DeployStatus.IN_PROGRESS
        d.stages[0].started_at = time.time()
        return d

    def report_health(
        self, installation_id: str, deploy_id: str, health_score: float,
    ) -> CanaryStage:
        d = self._get(installation_id, deploy_id)
        if d.status != DeployStatus.IN_PROGRESS:
            raise ValueError("Deploy not in progress")
        stage = d.stages[d.current_stage]
        stage.healthy = health_score >= stage.health_threshold
        return stage

    def advance(self, installation_id: str, deploy_id: str) -> CanaryDeploy:
        d = self._get(installation_id, deploy_id)
        if d.status != DeployStatus.IN_PROGRESS:
            raise ValueError("Deploy not in progress")
        stage = d.stages[d.current_stage]
        if stage.healthy is not True:
            raise ValueError("Current stage not healthy, cannot advance")

        if d.current_stage + 1 >= len(d.stages):
            d.status = DeployStatus.COMPLETED
        else:
            d.current_stage += 1
            d.stages[d.current_stage].started_at = time.time()
        return d

    def rollback(self, installation_id: str, deploy_id: str, reason: str = "") -> CanaryDeploy:
        d = self._get(installation_id, deploy_id)
        if d.status not in (DeployStatus.IN_PROGRESS, DeployStatus.PENDING):
            raise ValueError("Deploy cannot be rolled back")
        d.status = DeployStatus.ROLLED_BACK
        return d

    def current_traffic(self, installation_id: str, deploy_id: str) -> float:
        d = self._get(installation_id, deploy_id)
        if d.status != DeployStatus.IN_PROGRESS:
            return 0.0
        return d.stages[d.current_stage].traffic_pct

    def get_deploy(self, installation_id: str, deploy_id: str) -> CanaryDeploy:
        return self._get(installation_id, deploy_id)

    def list_deploys(self, installation_id: str) -> list[CanaryDeploy]:
        return [d for (inst, _), d in self._deploys.items() if inst == installation_id]

    def _get(self, installation_id: str, deploy_id: str) -> CanaryDeploy:
        key = (installation_id, deploy_id)
        d = self._deploys.get(key)
        if d is None:
            raise KeyError(f"Deploy {deploy_id} not found")
        return d
