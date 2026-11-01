"""Import validator — validate app import data structure."""

def validate_import_structure(data: dict) -> list[str]:
    errors = []
    if not isinstance(data, dict):
        return ["Import data must be an object"]
    if "export_version" not in data:
        errors.append("Missing export_version")
    if "app" not in data:
        errors.append("Missing app section")
    elif not isinstance(data["app"], dict):
        errors.append("App section must be an object")
    else:
        for field in ["name", "slug"]:
            if not data["app"].get(field):
                errors.append(f"Missing app.{field}")
    return errors
