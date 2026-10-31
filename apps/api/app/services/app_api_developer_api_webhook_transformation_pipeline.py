"""App API Developer Webhook Transformation Pipeline — transform payloads before delivery."""
from __future__ import annotations
from dataclasses import dataclass, field
import json
import structlog

log = structlog.get_logger()

@dataclass
class TransformStep:
    step_id: str
    operation: str  # "rename_field", "remove_field", "add_field", "map_value"
    config: dict[str, str] = field(default_factory=dict)

@dataclass
class TransformPipeline:
    pipeline_id: str
    steps: list[TransformStep] = field(default_factory=list)
    execution_count: int = 0
    error_count: int = 0

class AppAPIDeveloperAPIWebhookTransformationPipeline:
    def __init__(self) -> None:
        self._pipelines: dict[tuple[str, str], TransformPipeline] = {}

    def create(self, installation_id: str, pipeline_id: str, steps: list[dict]) -> TransformPipeline:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, pipeline_id)
        if key in self._pipelines: raise ValueError(f"Pipeline {pipeline_id} exists")
        parsed = [TransformStep(step_id=s["step_id"], operation=s["operation"], config=s.get("config", {})) for s in steps]
        valid_ops = {"rename_field", "remove_field", "add_field", "map_value"}
        for s in parsed:
            if s.operation not in valid_ops: raise ValueError(f"Invalid operation: {s.operation}")
        p = TransformPipeline(pipeline_id=pipeline_id, steps=parsed)
        self._pipelines[key] = p
        return p

    def execute(self, installation_id: str, pipeline_id: str, payload: dict) -> dict:
        key = (installation_id, pipeline_id)
        p = self._pipelines.get(key)
        if p is None: raise KeyError(f"Pipeline {pipeline_id} not found")
        p.execution_count += 1
        result = dict(payload)
        try:
            for step in p.steps:
                result = self._apply(step, result)
        except Exception:
            p.error_count += 1
            raise
        return result

    def _apply(self, step: TransformStep, payload: dict) -> dict:
        if step.operation == "rename_field":
            old, new = step.config.get("from", ""), step.config.get("to", "")
            if old in payload:
                payload[new] = payload.pop(old)
        elif step.operation == "remove_field":
            payload.pop(step.config.get("field", ""), None)
        elif step.operation == "add_field":
            payload[step.config.get("field", "")] = step.config.get("value", "")
        elif step.operation == "map_value":
            field_name = step.config.get("field", "")
            mapping = json.loads(step.config.get("mapping", "{}"))
            if field_name in payload and str(payload[field_name]) in mapping:
                payload[field_name] = mapping[str(payload[field_name])]
        return payload

    def list_pipelines(self, installation_id: str) -> list[TransformPipeline]:
        return [p for (inst, _), p in self._pipelines.items() if inst == installation_id]
