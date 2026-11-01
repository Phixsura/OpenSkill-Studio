"""Request Transformation Pipeline — chainable request/response transforms."""
from __future__ import annotations

import re
import structlog
from dataclasses import dataclass, field

logger = structlog.get_logger()


@dataclass
class Transform:
    transform_id: str
    name: str
    kind: str  # rename_field, remove_field, add_field, map_value, filter_keys
    config: dict = field(default_factory=dict)
    enabled: bool = True


@dataclass
class TransformPipeline:
    """Chain transforms on request/response payloads."""

    _transforms: dict[str, list[Transform]] = field(default_factory=dict)  # pipeline_id -> transforms

    def create_pipeline(self, pipeline_id: str) -> dict:
        if pipeline_id in self._transforms:
            raise ValueError(f"Pipeline {pipeline_id} already exists")
        self._transforms[pipeline_id] = []
        return {"pipeline_id": pipeline_id, "created": True}

    def add_transform(self, pipeline_id: str, transform: Transform) -> dict:
        if pipeline_id not in self._transforms:
            raise ValueError(f"Pipeline {pipeline_id} not found")
        valid_kinds = ("rename_field", "remove_field", "add_field", "map_value", "filter_keys")
        if transform.kind not in valid_kinds:
            raise ValueError(f"Invalid kind: {transform.kind}")
        self._transforms[pipeline_id].append(transform)
        logger.info("transform_added", pipeline_id=pipeline_id, kind=transform.kind)
        return {"pipeline_id": pipeline_id, "transform_count": len(self._transforms[pipeline_id])}

    def execute(self, pipeline_id: str, data: dict) -> dict:
        transforms = self._transforms.get(pipeline_id)
        if transforms is None:
            raise ValueError(f"Pipeline {pipeline_id} not found")
        result = dict(data)
        applied = []
        for t in transforms:
            if not t.enabled:
                continue
            if t.kind == "rename_field":
                old_name = t.config.get("from", "")
                new_name = t.config.get("to", "")
                if old_name in result:
                    result[new_name] = result.pop(old_name)
                    applied.append(t.transform_id)
            elif t.kind == "remove_field":
                field_name = t.config.get("field", "")
                if field_name in result:
                    del result[field_name]
                    applied.append(t.transform_id)
            elif t.kind == "add_field":
                field_name = t.config.get("field", "")
                value = t.config.get("value")
                if field_name:
                    result[field_name] = value
                    applied.append(t.transform_id)
            elif t.kind == "map_value":
                field_name = t.config.get("field", "")
                mapping = t.config.get("mapping", {})
                if field_name in result and str(result[field_name]) in mapping:
                    result[field_name] = mapping[str(result[field_name])]
                    applied.append(t.transform_id)
            elif t.kind == "filter_keys":
                allowed = set(t.config.get("keys", []))
                if allowed:
                    result = {k: v for k, v in result.items() if k in allowed}
                    applied.append(t.transform_id)
        return {"data": result, "applied": applied, "transform_count": len(applied)}

    def remove_transform(self, pipeline_id: str, transform_id: str) -> dict:
        transforms = self._transforms.get(pipeline_id, [])
        before = len(transforms)
        self._transforms[pipeline_id] = [t for t in transforms if t.transform_id != transform_id]
        return {"removed": before > len(self._transforms[pipeline_id])}

    def list_pipelines(self) -> list[dict]:
        return [
            {"pipeline_id": pid, "transform_count": len(ts),
             "enabled_count": sum(1 for t in ts if t.enabled)}
            for pid, ts in self._transforms.items()
        ]

    def get_pipeline(self, pipeline_id: str) -> list[dict]:
        transforms = self._transforms.get(pipeline_id, [])
        return [
            {"transform_id": t.transform_id, "name": t.name, "kind": t.kind,
             "enabled": t.enabled}
            for t in transforms
        ]
