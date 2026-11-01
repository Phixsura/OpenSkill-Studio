"""Consumer API Webhook Transform Pipeline — chain multiple transforms on webhook payloads."""
from __future__ import annotations
from dataclasses import dataclass, field
import json
import structlog

log = structlog.get_logger()

@dataclass
class TransformStep:
    step_id: str
    step_type: str  # "filter", "map", "enrich", "redact"
    config: dict[str, str] = field(default_factory=dict)
    order: int = 0
    enabled: bool = True

@dataclass
class Pipeline:
    pipeline_id: str
    webhook_id: str
    steps: list[TransformStep] = field(default_factory=list)

@dataclass
class PipelineResult:
    input_payload: dict
    output_payload: dict
    steps_executed: int
    steps_skipped: int

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiWebhookTransformPipeline:
    def __init__(self) -> None:
        self._pipelines: dict[tuple[str, str, str], Pipeline] = {}  # (inst, consumer, pipeline_id)

    def create_pipeline(self, installation_id: str, consumer_id: str, pipeline: Pipeline) -> Pipeline:
        if not installation_id:
            raise ValueError("installation_id is required")
        pipeline.steps.sort(key=lambda s: s.order)
        key = (installation_id, consumer_id, pipeline.pipeline_id)
        if key in self._pipelines:
            raise ValueError(f"Pipeline {pipeline.pipeline_id} already exists")
        self._pipelines[key] = pipeline
        return pipeline

    def execute(self, installation_id: str, consumer_id: str, pipeline_id: str, payload: dict) -> PipelineResult:
        key = (installation_id, consumer_id, pipeline_id)
        pipeline = self._pipelines.get(key)
        if not pipeline:
            raise ValueError("Pipeline not found")
        result = dict(payload)
        executed = 0
        skipped = 0
        for step in pipeline.steps:
            if not step.enabled:
                skipped += 1
                continue
            if step.step_type == "filter":
                fields = step.config.get("fields", "").split(",")
                result = {k: v for k, v in result.items() if k in fields}
            elif step.step_type == "map":
                for old_name, new_name in step.config.items():
                    if old_name in result:
                        result[new_name] = result.pop(old_name)
            elif step.step_type == "enrich":
                for k, v in step.config.items():
                    if k not in result:
                        result[k] = v
            elif step.step_type == "redact":
                for field_name in step.config.get("fields", "").split(","):
                    if field_name in result:
                        result[field_name] = "***"
            executed += 1
        return PipelineResult(input_payload=payload, output_payload=result, steps_executed=executed, steps_skipped=skipped)

    def list_pipelines(self, installation_id: str, consumer_id: str) -> list[Pipeline]:
        return [p for (inst, cid, _), p in self._pipelines.items() if inst == installation_id and cid == consumer_id]
