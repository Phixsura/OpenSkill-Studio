"""Export/Import — transfer app configurations between environments."""

import json
import hashlib
from datetime import datetime


def export_app_config(*, app_id: str, app: dict, include: list[str] | None = None) -> dict:
    exportable = {"manifest", "settings", "webhooks", "env_vars", "permissions"}
    sections = include or list(exportable)
    invalid = set(sections) - exportable
    if invalid:
        return {"error": f"Invalid sections: {', '.join(sorted(invalid))}"}
    exported = {s: app.get(s, {}) for s in sections}
    raw = json.dumps(exported, sort_keys=True)
    checksum = hashlib.sha256(raw.encode()).hexdigest()[:16]
    return {
        "app_id": app_id,
        "format_version": "1.0",
        "sections": sections,
        "data": exported,
        "checksum": checksum,
        "exported_at": datetime.utcnow().isoformat(),
        "size_bytes": len(raw),
    }


def validate_import(*, export_data: dict) -> dict:
    errors = []
    if export_data.get("format_version") != "1.0":
        errors.append("Unsupported format version")
    if not export_data.get("data"):
        errors.append("No data to import")
    if not export_data.get("checksum"):
        errors.append("Missing checksum")
    raw = json.dumps(export_data.get("data", {}), sort_keys=True)
    expected = hashlib.sha256(raw.encode()).hexdigest()[:16]
    if export_data.get("checksum") != expected:
        errors.append("Checksum mismatch — data may be corrupted")
    return {"valid": len(errors) == 0, "errors": errors,
            "sections": list(export_data.get("data", {}).keys())}
