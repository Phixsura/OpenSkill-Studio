"""API Webhook Transform Pipeline — chain transformations on webhook payloads."""
from __future__ import annotations
from dataclasses import dataclass, field
import json
import structlog

log = structlog.get_logger()

@dataclass
class TransformStep:
    step_id: str
    transform_type: str  # "add_field", "remove_field", "rename_field", "wrap", "flatten"
    config: dict[str, str] = field(default_factory=dict)

@dataclass
class Pipeline:
    pipeline_id: str
    consumer_id: str
    steps: list[TransformStep] = field(default_factory=list)
    executions: int = 0

VALID_TRANSFORMS = {"add_field", "remove_field", "rename_field", "wrap", "flatten"}

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiWebhookTransformPipeline:
    def __init__(self) -> None:
        self._pipelines: dict[tuple[str, str], Pipeline] = {}

    def create_pipeline(self, installation_id: str, pipeline_id: str, consumer_id: str, steps: list[TransformStep]) -> Pipeline:
        if not installation_id: raise ValueError("installation_id is required")
        if not steps: raise ValueError("Pipeline must have at least one step")
        for s in steps:
            if s.transform_type not in VALID_TRANSFORMS: raise ValueError(f"Invalid transform: {s.transform_type}")
        key = (installation_id, pipeline_id)
        if key in self._pipelines: raise ValueError(f"Pipeline {pipeline_id} already exists")
        p = Pipeline(pipeline_id=pipeline_id, consumer_id=consumer_id, steps=steps)
        self._pipelines[key] = p
        return p

    def execute(self, installation_id: str, pipeline_id: str, payload: dict) -> dict:
        p = self._get(installation_id, pipeline_id)
        result = dict(payload)
        for step in p.steps:
            if step.transform_type == "add_field":
                result[step.config.get("field", "")] = step.config.get("value", "")
            elif step.transform_type == "remove_field":
                result.pop(step.config.get("field", ""), None)
            elif step.transform_type == "rename_field":
                old = step.config.get("from", "")
                new = step.config.get("to", "")
                if old in result: result[new] = result.pop(old)
            elif step.transform_type == "wrap":
                wrapper = step.config.get("key", "data")
                result = {wrapper: result}
            elif step.transform_type == "flatten" and "data" in result and isinstance(result["data"], dict):
                inner = result.pop("data")
                result.update(inner)
        p.executions += 1
        return result

    def list_pipelines(self, installation_id: str) -> list[Pipeline]:
        return [p for (inst, _), p in self._pipelines.items() if inst == installation_id]

    def _get(self, installation_id: str, pipeline_id: str) -> Pipeline:
        p = self._pipelines.get((installation_id, pipeline_id))
        if p is None: raise KeyError(f"Pipeline {pipeline_id} not found")
        return p
