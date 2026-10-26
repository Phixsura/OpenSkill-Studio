"""Data Mapper — transform data between connector formats.

Maps fields between source and target schemas using configurable
transformations: rename, type cast, default values, computed fields,
and nested path extraction.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum


class TransformType(str, Enum):
    RENAME = "rename"
    CAST = "cast"
    DEFAULT = "default"
    TEMPLATE = "template"
    EXTRACT = "extract"  # nested path like "user.name"
    CONCAT = "concat"
    UPPERCASE = "uppercase"
    LOWERCASE = "lowercase"


@dataclass
class FieldMapping:
    source_field: str
    target_field: str
    transform: TransformType = TransformType.RENAME
    transform_config: dict = field(default_factory=dict)


@dataclass
class DataMapping:
    mapping_id: str
    name: str
    source_connector: str
    target_connector: str
    field_mappings: list[FieldMapping] = field(default_factory=list)


class DataMapperService:
    """Transforms data between connector schemas."""

    def __init__(self):
        self._mappings: dict[str, DataMapping] = {}

    def create_mapping(self, mapping_id: str, name: str,
                       source: str, target: str,
                       fields: list[dict]) -> DataMapping:
        parsed = [
            FieldMapping(
                source_field=f["source"], target_field=f["target"],
                transform=TransformType(f.get("transform", "rename")),
                transform_config=f.get("config", {}),
            )
            for f in fields
        ]
        mapping = DataMapping(
            mapping_id=mapping_id, name=name,
            source_connector=source, target_connector=target,
            field_mappings=parsed,
        )
        self._mappings[mapping_id] = mapping
        return mapping

    def transform(self, mapping_id: str, source_data: dict) -> dict:
        mapping = self._mappings.get(mapping_id)
        if not mapping:
            raise ValueError("Mapping not found")

        result: dict = {}
        for fm in mapping.field_mappings:
            value = self._get_nested(source_data, fm.source_field)
            transformed = self._apply_transform(value, fm)
            self._set_nested(result, fm.target_field, transformed)

        return result

    def transform_batch(self, mapping_id: str,
                        records: list[dict]) -> list[dict]:
        return [self.transform(mapping_id, r) for r in records]

    def _get_nested(self, data: dict, path: str) -> object:
        parts = path.split(".")
        current: object = data
        for part in parts:
            if isinstance(current, dict):
                current = current.get(part)
            else:
                return None
        return current

    def _set_nested(self, data: dict, path: str, value: object) -> None:
        parts = path.split(".")
        current = data
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        current[parts[-1]] = value

    def _apply_transform(self, value: object, fm: FieldMapping) -> object:
        if fm.transform == TransformType.RENAME:
            return value
        elif fm.transform == TransformType.DEFAULT:
            return value if value is not None else fm.transform_config.get("default")
        elif fm.transform == TransformType.CAST:
            target_type = fm.transform_config.get("type", "string")
            try:
                if target_type == "string":
                    return str(value) if value is not None else ""
                elif target_type == "integer":
                    return int(value) if value is not None else 0
                elif target_type == "float":
                    return float(value) if value is not None else 0.0
                elif target_type == "boolean":
                    return bool(value)
            except (ValueError, TypeError):
                return fm.transform_config.get("fallback")
        elif fm.transform == TransformType.UPPERCASE:
            return str(value).upper() if value else ""
        elif fm.transform == TransformType.LOWERCASE:
            return str(value).lower() if value else ""
        elif fm.transform == TransformType.TEMPLATE:
            template = fm.transform_config.get("template", "")
            return template.replace("{value}", str(value or ""))
        elif fm.transform == TransformType.CONCAT:
            separator = fm.transform_config.get("separator", " ")
            fields = fm.transform_config.get("fields", [])
            if isinstance(value, dict):
                parts = [str(value.get(f, "")) for f in fields]
                return separator.join(parts)
        return value
