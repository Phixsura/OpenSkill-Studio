"""Webhook Transform — transform webhook payloads between formats.

Applies configurable transformations to incoming/outgoing webhooks:
field mapping, filtering, enrichment, format conversion, and templating.
"""
from __future__ import annotations
import json
import secrets
from dataclasses import dataclass, field
from enum import Enum


class TransformOp(str, Enum):
    MAP = "map"           # rename/move field
    FILTER = "filter"     # include/exclude fields
    ENRICH = "enrich"     # add static fields
    TEMPLATE = "template" # mustache-style template
    FLATTEN = "flatten"   # flatten nested objects
    WRAP = "wrap"         # wrap payload under a key


@dataclass
class TransformStep:
    operation: TransformOp
    config: dict = field(default_factory=dict)


@dataclass
class TransformPipeline:
    pipeline_id: str
    name: str
    event_type: str
    steps: list[TransformStep] = field(default_factory=list)
    enabled: bool = True
    execution_count: int = 0


class WebhookTransformService:
    """Applies transformation pipelines to webhook payloads."""

    def __init__(self):
        self._pipelines: dict[str, TransformPipeline] = {}

    def create_pipeline(self, name: str, event_type: str,
                        steps: list[dict]) -> TransformPipeline:
        pipeline_id = f"wtp_{secrets.token_urlsafe(8)}"
        parsed = [TransformStep(
            operation=TransformOp(s["op"]),
            config=s.get("config", {}),
        ) for s in steps]
        pipeline = TransformPipeline(
            pipeline_id=pipeline_id, name=name,
            event_type=event_type, steps=parsed,
        )
        self._pipelines[pipeline_id] = pipeline
        return pipeline

    def transform(self, pipeline_id: str, payload: dict) -> dict | None:
        pipeline = self._pipelines.get(pipeline_id)
        if not pipeline or not pipeline.enabled:
            return None

        result = dict(payload)
        for step in pipeline.steps:
            result = self._apply_step(step, result)

        pipeline.execution_count += 1
        return result

    def _apply_step(self, step: TransformStep, data: dict) -> dict:
        if step.operation == TransformOp.MAP:
            mappings = step.config.get("fields", {})
            result = {}
            for old_key, new_key in mappings.items():
                if old_key in data:
                    result[new_key] = data[old_key]
            # Keep unmapped fields
            for k, v in data.items():
                if k not in mappings:
                    result[k] = v
            return result

        elif step.operation == TransformOp.FILTER:
            include = step.config.get("include")
            exclude = step.config.get("exclude", [])
            if include:
                return {k: v for k, v in data.items() if k in include}
            return {k: v for k, v in data.items() if k not in exclude}

        elif step.operation == TransformOp.ENRICH:
            enrichments = step.config.get("fields", {})
            return {**data, **enrichments}

        elif step.operation == TransformOp.FLATTEN:
            prefix = step.config.get("prefix", "")
            return self._flatten_dict(data, prefix)

        elif step.operation == TransformOp.WRAP:
            key = step.config.get("key", "data")
            return {key: data}

        elif step.operation == TransformOp.TEMPLATE:
            template = step.config.get("template", {})
            return self._apply_template(template, data)

        return data

    def _flatten_dict(self, d: dict, prefix: str = "") -> dict:
        result = {}
        for k, v in d.items():
            key = f"{prefix}{k}" if prefix else k
            if isinstance(v, dict):
                result.update(self._flatten_dict(v, f"{key}_"))
            else:
                result[key] = v
        return result

    def _apply_template(self, template: dict, data: dict) -> dict:
        result = {}
        for key, value in template.items():
            if isinstance(value, str) and value.startswith("$."):
                path = value[2:]
                result[key] = data.get(path, None)
            else:
                result[key] = value
        return result

    def list_pipelines(self, event_type: str | None = None) -> list[TransformPipeline]:
        pipelines = list(self._pipelines.values())
        if event_type:
            pipelines = [p for p in pipelines if p.event_type == event_type]
        return pipelines
