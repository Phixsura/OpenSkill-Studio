"""App Data Pipeline — define and execute multi-step data processing pipelines.

Manages data pipelines for installed apps:
- Define pipeline stages (extract, transform, load)
- Execute stages in sequence
- Track per-stage status and timing
- Error handling with stage-level granularity
- Per-installation scoped pipelines
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum

import structlog

log = structlog.get_logger()


class StageStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class PipelineStage:
    """A stage in a data pipeline."""

    stage_id: str
    name: str
    stage_type: str  # "extract", "transform", "load", "validate", "custom"
    status: StageStatus = StageStatus.PENDING
    started_at: float | None = None
    completed_at: float | None = None
    duration_ms: float | None = None
    input_count: int = 0
    output_count: int = 0
    error: str | None = None


@dataclass
class Pipeline:
    """A data processing pipeline."""

    pipeline_id: str
    installation_id: str
    name: str
    stages: list[PipelineStage] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)

    @property
    def status(self) -> str:
        if any(s.status == StageStatus.FAILED for s in self.stages):
            return "failed"
        if any(s.status == StageStatus.RUNNING for s in self.stages):
            return "running"
        if all(s.status == StageStatus.COMPLETED for s in self.stages):
            return "completed"
        return "pending"

    @property
    def current_stage(self) -> PipelineStage | None:
        for s in self.stages:
            if s.status in (StageStatus.PENDING, StageStatus.RUNNING):
                return s
        return None


class AppDataPipeline:
    """Define and execute multi-step data processing pipelines."""

    def __init__(self) -> None:
        self._pipelines: dict[tuple[str, str], Pipeline] = {}

    def create_pipeline(
        self,
        installation_id: str,
        pipeline_id: str,
        name: str,
        stages: list[dict],
    ) -> Pipeline:
        """Create a pipeline with stages."""
        if not installation_id:
            raise ValueError("installation_id is required")
        if not pipeline_id:
            raise ValueError("pipeline_id is required")
        if not stages:
            raise ValueError("at least one stage is required")

        key = (installation_id, pipeline_id)
        if key in self._pipelines:
            raise ValueError(f"Pipeline {pipeline_id} already exists")

        stage_objs = [
            PipelineStage(
                stage_id=s.get("stage_id", f"stage-{i}"),
                name=s["name"],
                stage_type=s.get("type", "custom"),
            )
            for i, s in enumerate(stages)
        ]

        pipeline = Pipeline(
            pipeline_id=pipeline_id,
            installation_id=installation_id,
            name=name,
            stages=stage_objs,
        )
        self._pipelines[key] = pipeline
        return pipeline

    def start_stage(
        self,
        installation_id: str,
        pipeline_id: str,
        stage_id: str,
        input_count: int = 0,
        now: float | None = None,
    ) -> PipelineStage:
        """Mark a stage as running."""
        pipeline = self._get(installation_id, pipeline_id)
        stage = self._find_stage(pipeline, stage_id)
        if stage.status != StageStatus.PENDING:
            raise ValueError(f"Cannot start stage in {stage.status} state")
        stage.status = StageStatus.RUNNING
        stage.started_at = now or time.time()
        stage.input_count = input_count
        return stage

    def complete_stage(
        self,
        installation_id: str,
        pipeline_id: str,
        stage_id: str,
        output_count: int = 0,
        now: float | None = None,
    ) -> PipelineStage:
        """Mark a stage as completed."""
        pipeline = self._get(installation_id, pipeline_id)
        stage = self._find_stage(pipeline, stage_id)
        if stage.status != StageStatus.RUNNING:
            raise ValueError(f"Cannot complete stage in {stage.status} state")
        now = now or time.time()
        stage.status = StageStatus.COMPLETED
        stage.completed_at = now
        stage.output_count = output_count
        stage.duration_ms = (now - stage.started_at) * 1000 if stage.started_at else 0
        return stage

    def fail_stage(
        self,
        installation_id: str,
        pipeline_id: str,
        stage_id: str,
        error: str = "",
        now: float | None = None,
    ) -> PipelineStage:
        """Mark a stage as failed. Remaining stages become skipped."""
        pipeline = self._get(installation_id, pipeline_id)
        stage = self._find_stage(pipeline, stage_id)
        now = now or time.time()
        stage.status = StageStatus.FAILED
        stage.completed_at = now
        stage.error = error
        if stage.started_at:
            stage.duration_ms = (now - stage.started_at) * 1000

        # Skip remaining stages
        found = False
        for s in pipeline.stages:
            if s.stage_id == stage_id:
                found = True
                continue
            if found and s.status == StageStatus.PENDING:
                s.status = StageStatus.SKIPPED

        return stage

    def get_pipeline(self, installation_id: str, pipeline_id: str) -> Pipeline:
        return self._get(installation_id, pipeline_id)

    def list_pipelines(self, installation_id: str) -> list[Pipeline]:
        return [
            p for (inst, _), p in self._pipelines.items()
            if inst == installation_id
        ]

    def _get(self, installation_id: str, pipeline_id: str) -> Pipeline:
        key = (installation_id, pipeline_id)
        p = self._pipelines.get(key)
        if p is None:
            raise KeyError(f"Pipeline {pipeline_id} not found")
        return p

    def _find_stage(self, pipeline: Pipeline, stage_id: str) -> PipelineStage:
        for s in pipeline.stages:
            if s.stage_id == stage_id:
                return s
        raise KeyError(f"Stage {stage_id} not found")
