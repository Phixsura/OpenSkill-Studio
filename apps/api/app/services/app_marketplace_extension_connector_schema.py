"""Connector Schema Validator — validate connector configurations against schemas.

Ensures connector inputs/outputs conform to declared schemas, validates
field types, required fields, default values, and provides detailed
validation error messages.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum


class FieldType(str, Enum):
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    ARRAY = "array"
    OBJECT = "object"
    EMAIL = "email"
    URL = "url"
    DATE = "date"


TYPE_VALIDATORS = {
    FieldType.STRING: lambda v: isinstance(v, str),
    FieldType.INTEGER: lambda v: isinstance(v, int) and not isinstance(v, bool),
    FieldType.FLOAT: lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
    FieldType.BOOLEAN: lambda v: isinstance(v, bool),
    FieldType.ARRAY: lambda v: isinstance(v, list),
    FieldType.OBJECT: lambda v: isinstance(v, dict),
    FieldType.EMAIL: lambda v: isinstance(v, str) and "@" in v and "." in v.split("@")[-1],
    FieldType.URL: lambda v: isinstance(v, str) and v.startswith(("http://", "https://")),
    FieldType.DATE: lambda v: isinstance(v, str) and len(v) == 10 and v[4] == "-" and v[7] == "-",
}


@dataclass
class SchemaField:
    name: str
    field_type: FieldType
    required: bool = True
    default: object = None
    description: str = ""
    min_length: int | None = None
    max_length: int | None = None
    enum_values: list[str] | None = None


@dataclass
class ConnectorSchema:
    connector_id: str
    version: str
    input_fields: list[SchemaField] = field(default_factory=list)
    output_fields: list[SchemaField] = field(default_factory=list)


@dataclass
class ValidationResult:
    valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    coerced_values: dict = field(default_factory=dict)


class ConnectorSchemaService:
    """Validates connector data against declared schemas."""

    def __init__(self):
        self._schemas: dict[str, ConnectorSchema] = {}

    def register_schema(self, connector_id: str, version: str,
                        input_fields: list[dict],
                        output_fields: list[dict] | None = None) -> ConnectorSchema:
        inputs = [SchemaField(
            name=f["name"], field_type=FieldType(f["type"]),
            required=f.get("required", True), default=f.get("default"),
            description=f.get("description", ""),
            min_length=f.get("min_length"), max_length=f.get("max_length"),
            enum_values=f.get("enum"),
        ) for f in input_fields]

        outputs = [SchemaField(
            name=f["name"], field_type=FieldType(f["type"]),
            required=f.get("required", True),
        ) for f in (output_fields or [])]

        schema = ConnectorSchema(
            connector_id=connector_id, version=version,
            input_fields=inputs, output_fields=outputs,
        )
        self._schemas[connector_id] = schema
        return schema

    def validate(self, connector_id: str, data: dict,
                 direction: str = "input") -> ValidationResult:
        schema = self._schemas.get(connector_id)
        if not schema:
            return ValidationResult(valid=False, errors=["Schema not found"])

        fields = schema.input_fields if direction == "input" else schema.output_fields
        errors: list[str] = []
        warnings: list[str] = []
        coerced: dict = {}

        field_map = {f.name: f for f in fields}
        # Check unknown fields
        for key in data:
            if key not in field_map:
                warnings.append(f"Unknown field: {key}")

        for sf in fields:
            value = data.get(sf.name)
            if value is None:
                if sf.required:
                    if sf.default is not None:
                        coerced[sf.name] = sf.default
                    else:
                        errors.append(f"Required field missing: {sf.name}")
                continue

            validator = TYPE_VALIDATORS.get(sf.field_type)
            if validator and not validator(value):
                errors.append(f"{sf.name}: expected {sf.field_type.value}, got {type(value).__name__}")
                continue

            if sf.min_length is not None and isinstance(value, str) and len(value) < sf.min_length:
                errors.append(f"{sf.name}: min length {sf.min_length}, got {len(value)}")
            if sf.max_length is not None and isinstance(value, str) and len(value) > sf.max_length:
                errors.append(f"{sf.name}: max length {sf.max_length}, got {len(value)}")
            if sf.enum_values and str(value) not in sf.enum_values:
                errors.append(f"{sf.name}: must be one of {sf.enum_values}")

        return ValidationResult(valid=len(errors) == 0, errors=errors,
                                warnings=warnings, coerced_values=coerced)
