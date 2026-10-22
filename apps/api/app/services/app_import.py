"""App import service — import exported app configurations.

Complements the export service for backup/migration workflows.
Validates imported data against current platform schema before applying.
"""

import structlog

from app.services.manifest_validator import validate_manifest

log = structlog.get_logger()


def validate_import_data(data: dict) -> dict:
    """Validate an app export before importing.

    Returns a validation report with errors and warnings.
    """
    report = {
        "valid": True,
        "errors": [],
        "warnings": [],
    }

    # Check export version
    if data.get("export_version") != "1.0":
        report["warnings"].append(
            f"Unknown export version: {data.get('export_version')}. Expected 1.0."
        )

    # Validate app block
    app_data = data.get("app")
    if not isinstance(app_data, dict):
        report["errors"].append("Missing 'app' block in import data")
        report["valid"] = False
        return report

    if not app_data.get("name"):
        report["errors"].append("app.name is required")
        report["valid"] = False

    if not app_data.get("slug"):
        report["errors"].append("app.slug is required")
        report["valid"] = False

    # Validate versions
    versions = data.get("versions", [])
    if not isinstance(versions, list):
        report["errors"].append("'versions' must be a list")
        report["valid"] = False
    else:
        for i, v in enumerate(versions):
            if not isinstance(v, dict):
                report["errors"].append(f"versions[{i}] must be an object")
                continue
            if not v.get("version"):
                report["errors"].append(f"versions[{i}].version is required")
            if not v.get("content_hash"):
                report["errors"].append(f"versions[{i}].content_hash is required")

            # Validate manifest if present
            manifest = v.get("manifest")
            if manifest:
                result = validate_manifest(manifest)
                if not result.valid:
                    for err in result.errors:
                        report["warnings"].append(
                            f"versions[{i}] manifest: {err}"
                        )

    # Validate UI extensions
    ui_ext = data.get("ui_extensions", [])
    if isinstance(ui_ext, list):
        for i, ext in enumerate(ui_ext):
            if not isinstance(ext, dict):
                continue
            if not ext.get("surface"):
                report["warnings"].append(f"ui_extensions[{i}].surface missing")
            if not ext.get("entry_path"):
                report["warnings"].append(f"ui_extensions[{i}].entry_path missing")

    if report["errors"]:
        report["valid"] = False

    return report


def prepare_import_plan(data: dict) -> dict:
    """Create an import plan showing what would be created/updated.

    Does not execute — returns a preview for user confirmation.
    """
    app_data = data.get("app", {})
    versions = data.get("versions", [])
    ui_ext = data.get("ui_extensions", [])

    return {
        "plan": {
            "app": {
                "action": "create",
                "name": app_data.get("name"),
                "slug": app_data.get("slug"),
                "category": app_data.get("category"),
            },
            "versions": [
                {
                    "action": "create",
                    "version": v.get("version"),
                    "has_manifest": bool(v.get("manifest")),
                }
                for v in versions
            ],
            "ui_extensions": [
                {
                    "action": "create",
                    "surface": ext.get("surface"),
                    "title": ext.get("title"),
                }
                for ext in ui_ext
            ],
        },
        "summary": {
            "app_count": 1,
            "version_count": len(versions),
            "ui_extension_count": len(ui_ext),
        },
    }
