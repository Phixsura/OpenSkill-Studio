"""Config schema — app configuration schema registry."""

import html

FIELD_TYPES = {"string", "integer", "float", "boolean", "select", "secret", "url", "email"}


def validate_schema(*, fields: list[dict]) -> dict:
    errors = []
    valid_fields = []
    names_seen: set[str] = set()
    for f in fields:
        name = f.get("name", "")
        ftype = f.get("type", "string")
        if not name:
            errors.append("Field missing name")
            continue
        if name in names_seen:
            errors.append(f"Duplicate field: {name}")
            continue
        if ftype not in FIELD_TYPES:
            errors.append(f"Unknown type '{ftype}' for field '{name}'")
            continue
        names_seen.add(name)
        valid_fields.append({
            "name": name,
            "type": ftype,
            "label": html.escape(f.get("label", name.replace("_", " ").title())),
            "required": f.get("required", False),
            "default": f.get("default"),
            "description": html.escape(f.get("description", "")),
            "options": f.get("options") if ftype == "select" else None,
        })
    return {"valid": len(errors) == 0, "errors": errors,
            "fields": valid_fields, "field_count": len(valid_fields),
            "required_count": sum(1 for f in valid_fields if f["required"])}
