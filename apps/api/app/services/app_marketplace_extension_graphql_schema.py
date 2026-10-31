"""Extension GraphQL Schema Builder — build and validate GraphQL schemas."""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class GqlField:
    name: str
    type: str  # String, Int, Float, Boolean, ID, [Type], Type!
    description: str = ""
    args: list[dict] = field(default_factory=list)


@dataclass
class GqlType:
    name: str
    kind: str = "type"  # type, input, enum, interface
    fields: list[GqlField] = field(default_factory=list)
    description: str = ""


class ExtGraphQLSchemaService:
    SCALAR_TYPES = {"String", "Int", "Float", "Boolean", "ID"}

    def __init__(self):
        self._types: dict[str, dict[str, GqlType]] = {}  # ext_id -> {name -> type}

    def add_type(self, extension_id: str, name: str, kind: str = "type",
                 description: str = "") -> GqlType:
        if extension_id not in self._types:
            self._types[extension_id] = {}
        t = GqlType(name=name, kind=kind, description=description)
        self._types[extension_id][name] = t
        return t

    def add_field(self, extension_id: str, type_name: str, field_name: str,
                  field_type: str, description: str = "") -> bool:
        t = self._types.get(extension_id, {}).get(type_name)
        if not t: return False
        t.fields.append(GqlField(name=field_name, type=field_type, description=description))
        return True

    def validate(self, extension_id: str) -> list[str]:
        errors = []
        types = self._types.get(extension_id, {})
        type_names = set(types.keys()) | self.SCALAR_TYPES
        for t in types.values():
            if not t.fields and t.kind != "enum":
                errors.append(f"{t.name} has no fields")
            for f in t.fields:
                base = f.type.replace("!", "").replace("[", "").replace("]", "")
                if base not in type_names:
                    errors.append(f"Unknown type '{base}' in {t.name}.{f.name}")
        return errors

    def to_sdl(self, extension_id: str) -> str:
        lines = []
        for t in self._types.get(extension_id, {}).values():
            if t.description:
                lines.append(f'"""{t.description}"""')
            lines.append(f"{t.kind} {t.name} {{")
            for f in t.fields:
                lines.append(f"  {f.name}: {f.type}")
            lines.append("}\n")
        return "\n".join(lines)
