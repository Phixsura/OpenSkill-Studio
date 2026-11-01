"""Consumer API Webhook Transformer — payload transformation pipeline."""
from __future__ import annotations

import structlog
from dataclasses import dataclass, field

logger = structlog.get_logger()

TRANSFORM_OPS = ("rename", "remove", "add", "flatten", "wrap", "extract")


@dataclass
class TransformOp:
    op: str
    config: dict = field(default_factory=dict)


@dataclass
class WebhookTransformer:
    """Transform webhook payloads through configurable pipelines."""

    _pipelines: dict[str, list[TransformOp]] = field(default_factory=dict)
    _transform_count: int = 0

    def create_pipeline(self, pipeline_id: str, ops: list[TransformOp]) -> dict:
        if pipeline_id in self._pipelines:
            raise ValueError(f"Pipeline {pipeline_id} already exists")
        for op in ops:
            if op.op not in TRANSFORM_OPS:
                raise ValueError(f"Invalid op: {op.op}")
        self._pipelines[pipeline_id] = ops
        logger.info("transform_pipeline_created", pipeline_id=pipeline_id)
        return {"pipeline_id": pipeline_id, "ops": len(ops)}

    def transform(self, pipeline_id: str, payload: dict) -> dict:
        ops = self._pipelines.get(pipeline_id)
        if ops is None:
            raise ValueError(f"Pipeline {pipeline_id} not found")
        result = dict(payload)
        applied = []
        for op in ops:
            if op.op == "rename":
                old = op.config.get("from", "")
                new = op.config.get("to", "")
                if old in result:
                    result[new] = result.pop(old)
                    applied.append("rename")
            elif op.op == "remove":
                field_name = op.config.get("field", "")
                if field_name in result:
                    del result[field_name]
                    applied.append("remove")
            elif op.op == "add":
                field_name = op.config.get("field", "")
                value = op.config.get("value")
                if field_name:
                    result[field_name] = value
                    applied.append("add")
            elif op.op == "flatten":
                prefix = op.config.get("field", "")
                if prefix in result and isinstance(result[prefix], dict):
                    nested = result.pop(prefix)
                    for k, v in nested.items():
                        result[f"{prefix}_{k}"] = v
                    applied.append("flatten")
            elif op.op == "wrap":
                wrapper = op.config.get("key", "data")
                result = {wrapper: result}
                applied.append("wrap")
            elif op.op == "extract":
                field_name = op.config.get("field", "")
                if field_name in result and isinstance(result[field_name], dict):
                    result = result[field_name]
                    applied.append("extract")
        self._transform_count += 1
        return {"payload": result, "applied": applied, "ops_applied": len(applied)}

    def delete_pipeline(self, pipeline_id: str) -> dict:
        if pipeline_id in self._pipelines:
            del self._pipelines[pipeline_id]
            return {"deleted": True}
        return {"deleted": False}

    def list_pipelines(self) -> list[dict]:
        return [
            {"pipeline_id": pid, "ops": len(ops)}
            for pid, ops in self._pipelines.items()
        ]

    def get_stats(self) -> dict:
        return {
            "total_pipelines": len(self._pipelines),
            "total_transforms": self._transform_count,
        }
