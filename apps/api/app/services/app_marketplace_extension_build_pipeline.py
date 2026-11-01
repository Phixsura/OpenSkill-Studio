"""Build Pipeline — CI/CD build pipeline for extension packaging.

Manages build stages (lint, test, bundle, publish) with artifact
tracking, build logs, caching, and deployment gate checks.
"""
from __future__ import annotations
import secrets
import time
from dataclasses import dataclass, field
from enum import Enum


class BuildStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class StageType(str, Enum):
    LINT = "lint"
    TEST = "test"
    BUILD = "build"
    SECURITY_SCAN = "security_scan"
    PACKAGE = "package"
    PUBLISH = "publish"


@dataclass
class BuildStage:
    name: str
    stage_type: StageType
    status: BuildStatus = BuildStatus.QUEUED
    duration_ms: float = 0.0
    log: str = ""
    exit_code: int = 0


@dataclass
class BuildRun:
    build_id: str
    extension_id: str
    version: str
    trigger: str  # push, manual, schedule
    status: BuildStatus = BuildStatus.QUEUED
    stages: list[BuildStage] = field(default_factory=list)
    started_at: float = 0.0
    finished_at: float = 0.0
    artifact_url: str = ""


class BuildPipelineService:
    """Manages CI/CD build pipelines for extensions."""

    DEFAULT_STAGES = [StageType.LINT, StageType.TEST, StageType.BUILD,
                      StageType.SECURITY_SCAN, StageType.PACKAGE]

    def __init__(self):
        self._builds: dict[str, BuildRun] = {}

    def create_build(self, extension_id: str, version: str,
                     trigger: str = "push",
                     stages: list[StageType] | None = None) -> BuildRun:
        build_id = f"bld_{secrets.token_urlsafe(10)}"
        stage_list = [BuildStage(name=st.value, stage_type=st)
                      for st in (stages or self.DEFAULT_STAGES)]
        build = BuildRun(
            build_id=build_id, extension_id=extension_id,
            version=version, trigger=trigger, stages=stage_list,
        )
        self._builds[build_id] = build
        return build

    def start_build(self, build_id: str) -> bool:
        build = self._builds.get(build_id)
        if not build or build.status != BuildStatus.QUEUED:
            return False
        build.status = BuildStatus.RUNNING
        build.started_at = time.time()
        if build.stages:
            build.stages[0].status = BuildStatus.RUNNING
        return True

    def complete_stage(self, build_id: str, stage_index: int,
                       passed: bool, log: str = "",
                       duration_ms: float = 0) -> dict:
        build = self._builds.get(build_id)
        if not build or build.status != BuildStatus.RUNNING:
            return {"ok": False, "error": "Build not running"}
        if stage_index >= len(build.stages):
            return {"ok": False, "error": "Invalid stage index"}

        stage = build.stages[stage_index]
        stage.status = BuildStatus.PASSED if passed else BuildStatus.FAILED
        stage.duration_ms = duration_ms
        stage.log = log
        stage.exit_code = 0 if passed else 1

        if not passed:
            build.status = BuildStatus.FAILED
            build.finished_at = time.time()
            return {"ok": True, "build_status": "failed", "failed_stage": stage.name}

        # Start next stage
        if stage_index + 1 < len(build.stages):
            build.stages[stage_index + 1].status = BuildStatus.RUNNING
        else:
            build.status = BuildStatus.PASSED
            build.finished_at = time.time()
            build.artifact_url = f"https://artifacts.example.com/{build.extension_id}/{build.version}.zip"

        return {"ok": True, "build_status": build.status.value}

    def cancel_build(self, build_id: str) -> bool:
        build = self._builds.get(build_id)
        if not build or build.status not in (BuildStatus.QUEUED, BuildStatus.RUNNING):
            return False
        build.status = BuildStatus.CANCELLED
        build.finished_at = time.time()
        return True

    def get_build(self, build_id: str) -> BuildRun | None:
        return self._builds.get(build_id)

    def list_builds(self, extension_id: str, limit: int = 20) -> list[BuildRun]:
        builds = [b for b in self._builds.values() if b.extension_id == extension_id]
        builds.sort(key=lambda b: b.started_at or 0, reverse=True)
        return builds[:limit]

    def get_stats(self, extension_id: str) -> dict:
        builds = [b for b in self._builds.values() if b.extension_id == extension_id]
        passed = sum(1 for b in builds if b.status == BuildStatus.PASSED)
        total = len(builds)
        return {
            "total_builds": total,
            "passed": passed,
            "failed": sum(1 for b in builds if b.status == BuildStatus.FAILED),
            "pass_rate": round(passed / total * 100, 1) if total else 0,
        }
