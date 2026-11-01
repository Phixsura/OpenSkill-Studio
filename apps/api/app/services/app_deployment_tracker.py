"""App Deployment Tracker — track app deployment versions across environments.

Tracks the lifecycle of app deployments:
- Register deployments per environment (staging, production, etc.)
- Track status: pending → deploying → deployed → rolled_back / failed
- Rollback support with history
- Per-installation scoped deployments
- Version comparison across environments
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum

import structlog

log = structlog.get_logger()


class DeployStatus(str, Enum):
    PENDING = "pending"
    DEPLOYING = "deploying"
    DEPLOYED = "deployed"
    ROLLED_BACK = "rolled_back"
    FAILED = "failed"


@dataclass
class Deployment:
    """A single deployment record."""

    deployment_id: str
    installation_id: str
    environment: str
    version: str
    status: DeployStatus = DeployStatus.PENDING
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    rolled_back_to: str | None = None  # version rolled back to
    error_message: str | None = None


@dataclass
class EnvironmentStatus:
    """Current deployment status for an environment."""

    environment: str
    current_version: str | None
    last_deployment: Deployment | None
    deployment_count: int


class AppDeploymentTracker:
    """Track app deployments across environments."""

    def __init__(self) -> None:
        # (installation_id, deployment_id) → Deployment
        self._deployments: dict[tuple[str, str], Deployment] = {}
        # Ordered history per (installation_id, environment)
        self._history: dict[tuple[str, str], list[str]] = {}

    def create_deployment(
        self,
        installation_id: str,
        deployment_id: str,
        environment: str,
        version: str,
    ) -> Deployment:
        """Register a new deployment."""
        if not installation_id:
            raise ValueError("installation_id is required")
        if not deployment_id:
            raise ValueError("deployment_id is required")
        if not environment:
            raise ValueError("environment is required")
        if not version:
            raise ValueError("version is required")

        dep = Deployment(
            deployment_id=deployment_id,
            installation_id=installation_id,
            environment=environment,
            version=version,
        )
        key = (installation_id, deployment_id)
        self._deployments[key] = dep

        hist_key = (installation_id, environment)
        self._history.setdefault(hist_key, []).append(deployment_id)

        log.info("deployment.created", deployment_id=deployment_id,
                 environment=environment, version=version)
        return dep

    def start_deployment(self, installation_id: str, deployment_id: str) -> Deployment:
        """Mark deployment as deploying."""
        dep = self._get(installation_id, deployment_id)
        if dep.status != DeployStatus.PENDING:
            raise ValueError(f"Cannot start deployment in {dep.status} state")
        dep.status = DeployStatus.DEPLOYING
        dep.updated_at = time.time()
        return dep

    def complete_deployment(self, installation_id: str, deployment_id: str) -> Deployment:
        """Mark deployment as successfully deployed."""
        dep = self._get(installation_id, deployment_id)
        if dep.status != DeployStatus.DEPLOYING:
            raise ValueError(f"Cannot complete deployment in {dep.status} state")
        dep.status = DeployStatus.DEPLOYED
        dep.updated_at = time.time()
        log.info("deployment.completed", deployment_id=deployment_id,
                 version=dep.version, environment=dep.environment)
        return dep

    def fail_deployment(self, installation_id: str, deployment_id: str,
                        error: str = "") -> Deployment:
        """Mark deployment as failed."""
        dep = self._get(installation_id, deployment_id)
        if dep.status not in (DeployStatus.PENDING, DeployStatus.DEPLOYING):
            raise ValueError(f"Cannot fail deployment in {dep.status} state")
        dep.status = DeployStatus.FAILED
        dep.error_message = error
        dep.updated_at = time.time()
        log.warning("deployment.failed", deployment_id=deployment_id, error=error)
        return dep

    def rollback(self, installation_id: str, deployment_id: str,
                 rollback_to_version: str) -> Deployment:
        """Roll back a deployed deployment."""
        dep = self._get(installation_id, deployment_id)
        if dep.status != DeployStatus.DEPLOYED:
            raise ValueError(f"Cannot roll back deployment in {dep.status} state")
        dep.status = DeployStatus.ROLLED_BACK
        dep.rolled_back_to = rollback_to_version
        dep.updated_at = time.time()
        log.info("deployment.rolled_back", deployment_id=deployment_id,
                 from_version=dep.version, to_version=rollback_to_version)
        return dep

    def get_deployment(self, installation_id: str, deployment_id: str) -> Deployment:
        return self._get(installation_id, deployment_id)

    def get_environment_status(self, installation_id: str,
                               environment: str) -> EnvironmentStatus:
        """Get current status of an environment."""
        hist_key = (installation_id, environment)
        dep_ids = self._history.get(hist_key, [])

        if not dep_ids:
            return EnvironmentStatus(
                environment=environment,
                current_version=None,
                last_deployment=None,
                deployment_count=0,
            )

        last_dep = self._deployments[(installation_id, dep_ids[-1])]
        current = last_dep.version if last_dep.status == DeployStatus.DEPLOYED else None
        # If rolled back, current is the rollback target
        if last_dep.status == DeployStatus.ROLLED_BACK:
            current = last_dep.rolled_back_to

        return EnvironmentStatus(
            environment=environment,
            current_version=current,
            last_deployment=last_dep,
            deployment_count=len(dep_ids),
        )

    def list_history(self, installation_id: str, environment: str,
                     limit: int = 10) -> list[Deployment]:
        """List deployment history for an environment, newest first."""
        hist_key = (installation_id, environment)
        dep_ids = self._history.get(hist_key, [])
        results = []
        for did in reversed(dep_ids[-limit:]):
            results.append(self._deployments[(installation_id, did)])
        return results

    def compare_environments(self, installation_id: str,
                             environments: list[str]) -> dict[str, str | None]:
        """Compare current versions across environments."""
        result: dict[str, str | None] = {}
        for env in environments:
            status = self.get_environment_status(installation_id, env)
            result[env] = status.current_version
        return result

    def _get(self, installation_id: str, deployment_id: str) -> Deployment:
        key = (installation_id, deployment_id)
        dep = self._deployments.get(key)
        if dep is None:
            raise KeyError(f"Deployment {deployment_id} not found")
        return dep
