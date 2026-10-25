"""Publish Pipeline — orchestrate the full extension publishing workflow.

Coordinates content validation, security scanning, compatibility check,
version management, and marketplace listing in a single pipeline.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class PipelineStage(str, Enum):
    VALIDATE = "validate"
    SECURITY_SCAN = "security_scan"
    COMPATIBILITY = "compatibility"
    BUILD = "build"
    PUBLISH = "publish"


class StageResult(str, Enum):
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    RUNNING = "running"


@dataclass
class StageOutcome:
    stage: PipelineStage
    result: StageResult
    message: str = ""
    duration_ms: float = 0.0
    details: dict = field(default_factory=dict)


@dataclass
class PipelineRun:
    run_id: str
    extension_id: str
    version: str
    stages: list[StageOutcome] = field(default_factory=list)
    started_at: str = ""
    finished_at: str = ""
    overall_result: str = "pending"

    def __post_init__(self):
        if not self.started_at:
            self.started_at = datetime.now(timezone.utc).isoformat()


class PublishPipeline:
    """Orchestrates the extension publishing workflow."""

    def __init__(self):
        self._runs: dict[str, PipelineRun] = {}
        self._stage_handlers: dict[PipelineStage, callable] = {
            PipelineStage.VALIDATE: self._validate,
            PipelineStage.SECURITY_SCAN: self._security_scan,
            PipelineStage.COMPATIBILITY: self._compatibility_check,
            PipelineStage.BUILD: self._build,
            PipelineStage.PUBLISH: self._publish,
        }

    def _validate(self, ext_id: str, version: str, metadata: dict) -> StageOutcome:
        errors = []
        if not metadata.get("name"):
            errors.append("Missing name")
        if not metadata.get("description") or len(metadata.get("description", "")) < 10:
            errors.append("Description too short")
        if errors:
            return StageOutcome(PipelineStage.VALIDATE, StageResult.FAILED,
                                "; ".join(errors), details={"errors": errors})
        return StageOutcome(PipelineStage.VALIDATE, StageResult.PASSED, "Validation passed")

    def _security_scan(self, ext_id: str, version: str, metadata: dict) -> StageOutcome:
        code = metadata.get("code", "")
        issues = []
        if "eval(" in code:
            issues.append("eval() detected")
        if "exec(" in code:
            issues.append("exec() detected")
        if issues:
            return StageOutcome(PipelineStage.SECURITY_SCAN, StageResult.FAILED,
                                "Security issues found", details={"issues": issues})
        return StageOutcome(PipelineStage.SECURITY_SCAN, StageResult.PASSED, "No issues")

    def _compatibility_check(self, ext_id: str, version: str, metadata: dict) -> StageOutcome:
        min_ver = metadata.get("min_platform_version", "1.0.0")
        return StageOutcome(PipelineStage.COMPATIBILITY, StageResult.PASSED,
                            f"Compatible with platform >= {min_ver}")

    def _build(self, ext_id: str, version: str, metadata: dict) -> StageOutcome:
        return StageOutcome(PipelineStage.BUILD, StageResult.PASSED,
                            f"Built {ext_id}@{version}", duration_ms=150.0)

    def _publish(self, ext_id: str, version: str, metadata: dict) -> StageOutcome:
        return StageOutcome(PipelineStage.PUBLISH, StageResult.PASSED,
                            f"Published {ext_id}@{version} to marketplace")

    def run(self, run_id: str, extension_id: str, version: str,
            metadata: dict) -> PipelineRun:
        """Execute the full publish pipeline."""
        pipeline = PipelineRun(run_id=run_id, extension_id=extension_id, version=version)

        for stage in PipelineStage:
            handler = self._stage_handlers[stage]
            outcome = handler(extension_id, version, metadata)
            pipeline.stages.append(outcome)
            if outcome.result == StageResult.FAILED:
                pipeline.overall_result = "failed"
                pipeline.finished_at = datetime.now(timezone.utc).isoformat()
                self._runs[run_id] = pipeline
                return pipeline

        pipeline.overall_result = "success"
        pipeline.finished_at = datetime.now(timezone.utc).isoformat()
        self._runs[run_id] = pipeline
        return pipeline

    def get_run(self, run_id: str) -> PipelineRun | None:
        return self._runs.get(run_id)

    def list_runs(self, extension_id: str) -> list[PipelineRun]:
        return [r for r in self._runs.values() if r.extension_id == extension_id]
