"""Form builder — dynamic form schema for app configuration."""


FIELD_TYPES = {"text", "number", "email", "select", "checkbox", "textarea", "url", "password"}


def create_form_schema(*, title: str, fields: list[dict]) -> dict:
    validated = []
    errors = []
    for i, field in enumerate(fields):
        ftype = field.get("type", "text")
        if ftype not in FIELD_TYPES:
            errors.append(f"Field {i}: invalid type '{ftype}'")
            continue
        validated.append({
            "name": field["name"],
            "label": field.get("label", field["name"].replace("_", " ").title()),
            "type": ftype,
            "required": field.get("required", False),
            "placeholder": field.get("placeholder", ""),
            "options": field.get("options", []) if ftype == "select" else [],
            "default": field.get("default"),
        })
    return {
        "title": title,
        "fields": validated,
        "field_count": len(validated),
        "errors": errors,
        "valid": len(errors) == 0,
    }


def validate_form_data(*, schema: dict, data: dict) -> dict:
    errors = []
    for field in schema.get("fields", []):
        name = field["name"]
        value = data.get(name)
        if field["required"] and not value:
            errors.append({"field": name, "error": "Required field"})
        if field["type"] == "email" and value and "@" not in str(value):
            errors.append({"field": name, "error": "Invalid email"})
    return {"valid": len(errors) == 0, "errors": errors}
