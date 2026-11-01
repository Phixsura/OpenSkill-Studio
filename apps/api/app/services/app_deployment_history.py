"""App Deployment History — track deployment events.

Tracks deployment history:
- Record deployments with version, commit, deployer
- Track deployment duration
- Query by status or version
- Per-installation scoped history
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum

import structlog

log = structlog.get_logger()


class DeployResult(str, Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    ROLLBACK = "rollback"
    IN_PROGRESS = "in_progress"


@dataclass
class Deployment:
    """A deployment event."""

    deploy_id: str
    version: str
    commit_sha: str
    deployer: str
    result: DeployResult = DeployResult.IN_PROGRESS
    started_at: float = field(default_factory=time.time)
    finished_at: float | None = None
    error: str = ""

    @property
    def duration_seconds(self) -> float | None:
        if self.finished_at is None:
            return None
        return round(self.finished_at - self.started_at, 1)


class AppDeploymentHistory:
    """Track deployment events."""

    def __init__(self, max_entries: int = 500) -> None:
        self._max = max(1, max_entries)
        self._deploys: dict[str, list[Deployment]] = {}

    def start(
        self, installation_id: str, deploy_id: str, version: str,
        commit_sha: str, deployer: str,
    ) -> Deployment:
        if not installation_id:
            raise ValueError("installation_id is required")

        deploy = Deployment(
            deploy_id=deploy_id, version=version,
            commit_sha=commit_sha, deployer=deployer,
        )
        entries = self._deploys.setdefault(installation_id, [])
        entries.append(deploy)
        if len(entries) > self._max:
            self._deploys[installation_id] = entries[-self._max:]
        return deploy

    def finish(
        self, installation_id: str, deploy_id: str,
        result: DeployResult, error: str = "",
    ) -> Deployment:
        d = self._find(installation_id, deploy_id)
        d.result = result
        d.finished_at = time.time()
        d.error = error
        return d

    def recent(self, installation_id: str, limit: int = 20) -> list[Deployment]:
        return list(reversed(self._deploys.get(installation_id, [])[-limit:]))

    def by_result(self, installation_id: str, result: DeployResult) -> list[Deployment]:
        return [d for d in self._deploys.get(installation_id, []) if d.result == result]

    def success_rate(self, installation_id: str) -> float:
        deploys = [d for d in self._deploys.get(installation_id, []) if d.result != DeployResult.IN_PROGRESS]
        if not deploys:
            return 100.0
        successes = sum(1 for d in deploys if d.result == DeployResult.SUCCESS)
        return round(successes / len(deploys) * 100, 1)

    def count(self, installation_id: str) -> int:
        return len(self._deploys.get(installation_id, []))

    def _find(self, installation_id: str, deploy_id: str) -> Deployment:
        for d in self._deploys.get(installation_id, []):
            if d.deploy_id == deploy_id:
                return d
        raise KeyError(f"Deployment {deploy_id} not found")
