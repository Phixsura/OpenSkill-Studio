"""Data Pipeline — configurable ETL pipelines for connector data flows.

Defines multi-step data pipelines with extract, transform, load stages,
error handling per stage, execution metrics, and pipeline scheduling.
"""
from __future__ import annotations
import secrets
import time
from dataclasses import dataclass, field
from enum import Enum


class StageType(str, Enum):
    EXTRACT = "extract"
    TRANSFORM = "transform"
    LOAD = "load"
    VALIDATE = "validate"
    FILTER = "filter"


class PipelineStatus(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


@dataclass
class PipelineStage:
    name: str
    stage_type: StageType
    config: dict = field(default_factory=dict)
    status: str = "pending"
    records_in: int = 0
    records_out: int = 0
    error: str = ""
    duration_ms: float = 0.0


@dataclass
class DataPipeline:
    pipeline_id: str
    extension_id: str
    name: str
    stages: list[PipelineStage] = field(default_factory=list)
    status: PipelineStatus = PipelineStatus.IDLE
    total_records: int = 0
    run_count: int = 0
    last_run_duration_ms: float = 0.0
    created_at: float = 0.0

    def __post_init__(self):
        if not self.created_at:
            self.created_at = time.time()


class DataPipelineService:
    """Manages configurable ETL pipelines with stage-level tracking."""

    def __init__(self):
        self._pipelines: dict[str, DataPipeline] = {}

    def create(self, extension_id: str, name: str,
               stages: list[dict]) -> DataPipeline:
        parsed = [PipelineStage(
            name=s["name"], stage_type=StageType(s["type"]),
            config=s.get("config", {}),
        ) for s in stages]

        if not parsed:
            raise ValueError("Pipeline must have at least one stage")

        pipeline_id = f"pipe_{secrets.token_urlsafe(8)}"
        pipeline = DataPipeline(
            pipeline_id=pipeline_id, extension_id=extension_id,
            name=name, stages=parsed,
        )
        self._pipelines[pipeline_id] = pipeline
        return pipeline

    def execute(self, pipeline_id: str, input_records: list[dict]) -> dict:
        pipeline = self._pipelines.get(pipeline_id)
        if not pipeline:
            return {"ok": False, "error": "Pipeline not found"}
        if pipeline.status == PipelineStatus.RUNNING:
            return {"ok": False, "error": "Already running"}

        pipeline.status = PipelineStatus.RUNNING
        start = time.time()
        current_data = list(input_records)

        for stage in pipeline.stages:
            stage.status = "running"
            stage.records_in = len(current_data)
            stage_start = time.time()

            try:
                current_data = self._execute_stage(stage, current_data)
                stage.records_out = len(current_data)
                stage.status = "completed"
            except Exception as e:
                stage.status = "failed"
                stage.error = str(e)
                pipeline.status = PipelineStatus.FAILED
                pipeline.last_run_duration_ms = round((time.time() - start) * 1000, 1)
                return {"ok": False, "error": f"Stage '{stage.name}' failed: {e}",
                        "failed_stage": stage.name}
            finally:
                stage.duration_ms = round((time.time() - stage_start) * 1000, 1)

        pipeline.status = PipelineStatus.COMPLETED
        pipeline.total_records = len(current_data)
        pipeline.run_count += 1
        pipeline.last_run_duration_ms = round((time.time() - start) * 1000, 1)

        return {"ok": True, "records": len(current_data),
                "duration_ms": pipeline.last_run_duration_ms}

    def _execute_stage(self, stage: PipelineStage,
                       data: list[dict]) -> list[dict]:
        if stage.stage_type == StageType.FILTER:
            field_name = stage.config.get("field", "")
            value = stage.config.get("value")
            if field_name:
                return [r for r in data if r.get(field_name) == value]
            return data

        if stage.stage_type == StageType.VALIDATE:
            required = stage.config.get("required_fields", [])
            valid = []
            for r in data:
                if all(f in r for f in required):
                    valid.append(r)
            return valid

        if stage.stage_type == StageType.TRANSFORM:
            rename = stage.config.get("rename", {})
            result = []
            for r in data:
                new_r = {}
                for k, v in r.items():
                    new_r[rename.get(k, k)] = v
                result.append(new_r)
            return result

        # EXTRACT and LOAD pass through (in production would connect to sources)
        return data

    def get_pipeline(self, pipeline_id: str) -> DataPipeline | None:
        return self._pipelines.get(pipeline_id)

    def list_pipelines(self, extension_id: str) -> list[DataPipeline]:
        return [p for p in self._pipelines.values() if p.extension_id == extension_id]
