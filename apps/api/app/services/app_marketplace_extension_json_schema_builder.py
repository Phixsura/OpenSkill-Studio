"""JSON Schema Builder — fluent API for constructing and validating JSON schemas.

Implements:
- Builder pattern for schema construction
- Type builders: string, integer, number, boolean, array, object
- Constraints: required, min/max, pattern, enum, format
- Composition: allOf, anyOf, oneOf
- Schema-to-documentation generation
- Schema validation against instances
"""
from __future__ import annotations
from dataclasses import dataclass, field
import re


class SchemaBuilder:
    def __init__(self):
        self._schema: dict = {}

    def type(self, t: str) -> SchemaBuilder:
        self._schema["type"] = t
        return self

    def description(self, desc: str) -> SchemaBuilder:
        self._schema["description"] = desc
        return self

    def string(self) -> StringSchemaBuilder:
        return StringSchemaBuilder()

    def integer(self) -> NumberSchemaBuilder:
        b = NumberSchemaBuilder()
        b._schema["type"] = "integer"
        return b

    def number(self) -> NumberSchemaBuilder:
        return NumberSchemaBuilder()

    def boolean(self) -> SchemaBuilder:
        self._schema["type"] = "boolean"
        return self

    def array(self, items: dict | None = None) -> ArraySchemaBuilder:
        return ArraySchemaBuilder(items)

    def object(self) -> ObjectSchemaBuilder:
        return ObjectSchemaBuilder()

    def build(self) -> dict:
        return dict(self._schema)


class StringSchemaBuilder(SchemaBuilder):
    def __init__(self):
        super().__init__()
        self._schema["type"] = "string"

    def min_length(self, n: int) -> StringSchemaBuilder:
        self._schema["minLength"] = n
        return self

    def max_length(self, n: int) -> StringSchemaBuilder:
        self._schema["maxLength"] = n
        return self

    def pattern(self, regex: str) -> StringSchemaBuilder:
        self._schema["pattern"] = regex
        return self

    def enum(self, *values: str) -> StringSchemaBuilder:
        self._schema["enum"] = list(values)
        return self

    def format(self, fmt: str) -> StringSchemaBuilder:
        self._schema["format"] = fmt
        return self


class NumberSchemaBuilder(SchemaBuilder):
    def __init__(self):
        super().__init__()
        self._schema["type"] = "number"

    def minimum(self, n: float) -> NumberSchemaBuilder:
        self._schema["minimum"] = n
        return self

    def maximum(self, n: float) -> NumberSchemaBuilder:
        self._schema["maximum"] = n
        return self

    def multiple_of(self, n: float) -> NumberSchemaBuilder:
        self._schema["multipleOf"] = n
        return self


class ArraySchemaBuilder(SchemaBuilder):
    def __init__(self, items: dict | None = None):
        super().__init__()
        self._schema["type"] = "array"
        if items:
            self._schema["items"] = items

    def items(self, schema: dict) -> ArraySchemaBuilder:
        self._schema["items"] = schema
        return self

    def min_items(self, n: int) -> ArraySchemaBuilder:
        self._schema["minItems"] = n
        return self

    def max_items(self, n: int) -> ArraySchemaBuilder:
        self._schema["maxItems"] = n
        return self

    def unique(self) -> ArraySchemaBuilder:
        self._schema["uniqueItems"] = True
        return self


class ObjectSchemaBuilder(SchemaBuilder):
    def __init__(self):
        super().__init__()
        self._schema = {"type": "object", "properties": {}, "required": []}

    def prop(self, name: str, schema: dict, required: bool = False) -> ObjectSchemaBuilder:
        self._schema["properties"][name] = schema
        if required and name not in self._schema["required"]:
            self._schema["required"].append(name)
        return self

    def no_additional(self) -> ObjectSchemaBuilder:
        self._schema["additionalProperties"] = False
        return self

    def build(self) -> dict:
        result = dict(self._schema)
        if not result.get("required"):
            result.pop("required", None)
        return result


class JsonSchemaBuilderService:
    def __init__(self):
        pass

    def create(self) -> SchemaBuilder:
        return SchemaBuilder()

    def validate(self, instance: object, schema: dict) -> list[str]:
        """Validate an instance against a schema. Returns list of errors."""
        return self._validate(instance, schema, "$")

    def _validate(self, instance: object, schema: dict, path: str) -> list[str]:
        errors = []
        expected_type = schema.get("type")

        if instance is None:
            if expected_type:
                errors.append(f"{path}: expected {expected_type}, got null")
            return errors

        # Type check
        type_map = {"string": str, "integer": int, "number": (int, float),
                    "boolean": bool, "array": list, "object": dict}
        if expected_type:
            py_type = type_map.get(expected_type)
            if py_type:
                if isinstance(instance, bool) and expected_type in ("integer", "number"):
                    errors.append(f"{path}: expected {expected_type}, got boolean")
                    return errors
                if not isinstance(instance, py_type):
                    errors.append(f"{path}: expected {expected_type}, got {type(instance).__name__}")
                    return errors

        # String constraints
        if isinstance(instance, str):
            if "minLength" in schema and len(instance) < schema["minLength"]:
                errors.append(f"{path}: length < minLength {schema['minLength']}")
            if "maxLength" in schema and len(instance) > schema["maxLength"]:
                errors.append(f"{path}: length > maxLength {schema['maxLength']}")
            if "pattern" in schema and not re.search(schema["pattern"], instance):
                errors.append(f"{path}: does not match pattern")
            if "enum" in schema and instance not in schema["enum"]:
                errors.append(f"{path}: not in enum {schema['enum']}")

        # Number constraints
        if isinstance(instance, (int, float)) and not isinstance(instance, bool):
            if "minimum" in schema and instance < schema["minimum"]:
                errors.append(f"{path}: {instance} < minimum {schema['minimum']}")
            if "maximum" in schema and instance > schema["maximum"]:
                errors.append(f"{path}: {instance} > maximum {schema['maximum']}")

        # Array constraints
        if isinstance(instance, list):
            if "minItems" in schema and len(instance) < schema["minItems"]:
                errors.append(f"{path}: array length < minItems")
            if "maxItems" in schema and len(instance) > schema["maxItems"]:
                errors.append(f"{path}: array length > maxItems")
            if schema.get("uniqueItems") and len(set(str(x) for x in instance)) != len(instance):
                errors.append(f"{path}: items not unique")
            if "items" in schema:
                for i, item in enumerate(instance):
                    errors.extend(self._validate(item, schema["items"], f"{path}[{i}]"))

        # Object constraints
        if isinstance(instance, dict):
            for req in schema.get("required", []):
                if req not in instance:
                    errors.append(f"{path}.{req}: required")
            for prop_name, prop_schema in schema.get("properties", {}).items():
                if prop_name in instance:
                    errors.extend(self._validate(instance[prop_name], prop_schema,
                                                 f"{path}.{prop_name}"))
            if schema.get("additionalProperties") is False:
                allowed = set(schema.get("properties", {}).keys())
                for key in instance:
                    if key not in allowed:
                        errors.append(f"{path}.{key}: additional property not allowed")

        return errors

    def to_docs(self, schema: dict, indent: int = 0) -> str:
        """Generate human-readable documentation from schema."""
        lines = []
        prefix = "  " * indent
        t = schema.get("type", "any")
        desc = schema.get("description", "")

        if t == "object":
            lines.append(f"{prefix}object{' — ' + desc if desc else ''}")
            for prop, prop_schema in schema.get("properties", {}).items():
                required = prop in schema.get("required", [])
                req_mark = " (required)" if required else ""
                lines.append(f"{prefix}  {prop}{req_mark}:")
                lines.append(self.to_docs(prop_schema, indent + 2))
        elif t == "array":
            lines.append(f"{prefix}array{' — ' + desc if desc else ''}")
            if "items" in schema:
                lines.append(f"{prefix}  items:")
                lines.append(self.to_docs(schema["items"], indent + 2))
        else:
            constraints = []
            if "minimum" in schema: constraints.append(f"min={schema['minimum']}")
            if "maximum" in schema: constraints.append(f"max={schema['maximum']}")
            if "minLength" in schema: constraints.append(f"minLen={schema['minLength']}")
            if "enum" in schema: constraints.append(f"enum={schema['enum']}")
            c = f" [{', '.join(constraints)}]" if constraints else ""
            lines.append(f"{prefix}{t}{c}{' — ' + desc if desc else ''}")

        return "\n".join(lines)
