"""JSON schema form — auto-generate form fields from JSON Schema."""

import html

TYPE_MAP = {
    "string": "text", "integer": "number", "number": "number",
    "boolean": "checkbox", "array": "multi-select",
}


def schema_to_fields(*, schema: dict) -> dict:
    props = schema.get("properties", {})
    required = set(schema.get("required", []))
    fields = []
    for name, prop in props.items():
        field_type = TYPE_MAP.get(prop.get("type", "string"), "text")
        if prop.get("enum"):
            field_type = "select"
        fields.append({
            "name": name,
            "label": html.escape(prop.get("title", name.replace("_", " ").title())),
            "type": field_type,
            "required": name in required,
            "default": prop.get("default"),
            "description": html.escape(prop.get("description", "")),
            "enum": prop.get("enum"),
            "min": prop.get("minimum"),
            "max": prop.get("maximum"),
            "pattern": prop.get("pattern"),
        })
    return {"fields": fields, "total": len(fields),
            "required_count": sum(1 for f in fields if f["required"])}
