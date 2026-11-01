"""CI Integration — connect extension development with CI/CD pipelines.

Provides build triggers, status reporting, artifact management,
and deployment hooks for extension CI/CD workflows.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class BuildStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    CANCELED = "canceled"


@dataclass
class BuildStep:
    name: str
    status: BuildStatus = BuildStatus.QUEUED
    duration_ms: float = 0.0
    log: str = ""


@dataclass
class CIBuild:
    build_id: str
    extension_id: str
    version: str
    trigger: str  # "push", "pr", "manual", "schedule"
    branch: str
    commit_sha: str
    status: BuildStatus = BuildStatus.QUEUED
    steps: list[BuildStep] = field(default_factory=list)
    started_at: str = ""
    finished_at: str = ""
    artifacts: list[str] = field(default_factory=list)


class CIIntegration:
    """Manages CI/CD builds for extensions."""

    def __init__(self):
        self._builds: dict[str, CIBuild] = {}

    def create_build(self, build_id: str, extension_id: str, version: str,
                     trigger: str, branch: str, commit_sha: str,
                     steps: list[str] | None = None) -> CIBuild:
        """Create a new CI build."""
        default_steps = steps or ["install", "lint", "test", "build", "security_scan"]
        build = CIBuild(
            build_id=build_id, extension_id=extension_id, version=version,
            trigger=trigger, branch=branch, commit_sha=commit_sha,
            steps=[BuildStep(name=s) for s in default_steps],
            started_at=datetime.now(timezone.utc).isoformat(),
        )
        build.status = BuildStatus.RUNNING
        self._builds[build_id] = build
        return build

    def update_step(self, build_id: str, step_name: str,
                    status: BuildStatus, duration_ms: float = 0.0,
                    log: str = "") -> bool:
        """Update a build step's status."""
        build = self._builds.get(build_id)
        if not build:
            return False
        for step in build.steps:
            if step.name == step_name:
                step.status = status
                step.duration_ms = duration_ms
                step.log = log
                return True
        return False

    def finish_build(self, build_id: str) -> CIBuild | None:
        """Finalize build status based on step results."""
        build = self._builds.get(build_id)
        if not build:
            return None
        build.finished_at = datetime.now(timezone.utc).isoformat()
        if any(s.status == BuildStatus.FAILED for s in build.steps):
            build.status = BuildStatus.FAILED
        elif all(s.status == BuildStatus.PASSED for s in build.steps):
            build.status = BuildStatus.PASSED
        else:
            build.status = BuildStatus.CANCELED
        return build

    def add_artifact(self, build_id: str, artifact_path: str) -> bool:
        build = self._builds.get(build_id)
        if build:
            build.artifacts.append(artifact_path)
            return True
        return False

    def get_build(self, build_id: str) -> CIBuild | None:
        return self._builds.get(build_id)

    def list_builds(self, extension_id: str, status: BuildStatus | None = None) -> list[CIBuild]:
        builds = [b for b in self._builds.values() if b.extension_id == extension_id]
        if status:
            builds = [b for b in builds if b.status == status]
        return sorted(builds, key=lambda b: b.started_at, reverse=True)

    def get_build_summary(self, build_id: str) -> dict | None:
        build = self._builds.get(build_id)
        if not build:
            return None
        total_ms = sum(s.duration_ms for s in build.steps)
        return {
            "build_id": build_id, "status": build.status.value,
            "steps": len(build.steps),
            "passed": sum(1 for s in build.steps if s.status == BuildStatus.PASSED),
            "failed": sum(1 for s in build.steps if s.status == BuildStatus.FAILED),
            "total_duration_ms": round(total_ms, 2),
            "artifacts": len(build.artifacts),
        }
