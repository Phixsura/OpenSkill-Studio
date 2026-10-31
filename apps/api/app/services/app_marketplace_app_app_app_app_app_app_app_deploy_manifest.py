"""Deployment manifest validator — validate deployment manifests."""
from __future__ import annotations


def validate_manifest(manifest: dict) -> dict:
    errors = []
    required_fields = ["name", "version", "services"]
    for f in required_fields:
        if f not in manifest:
            errors.append({"field": f, "error": "missing_required_field"})
    if "services" in manifest:
        for i, svc in enumerate(manifest["services"]):
            if "name" not in svc:
                errors.append({"field": f"services[{i}].name", "error": "missing"})
            if "image" not in svc:
                errors.append({"field": f"services[{i}].image", "error": "missing"})
            replicas = svc.get("replicas", 1)
            if not isinstance(replicas, int) or replicas < 1:
                errors.append({"field": f"services[{i}].replicas", "error": "must be positive integer"})
    return {"valid": len(errors) == 0, "errors": errors, "services": len(manifest.get("services", []))}


def diff_manifests(old: dict, new: dict) -> dict:
    old_svcs = {s["name"]: s for s in old.get("services", [])}
    new_svcs = {s["name"]: s for s in new.get("services", [])}
    added = sorted(set(new_svcs) - set(old_svcs))
    removed = sorted(set(old_svcs) - set(new_svcs))
    changed = []
    for name in sorted(set(old_svcs) & set(new_svcs)):
        if old_svcs[name].get("image") != new_svcs[name].get("image"):
            changed.append({"service": name, "old_image": old_svcs[name].get("image"),
                            "new_image": new_svcs[name].get("image")})
    return {"added": added, "removed": removed, "changed": changed,
            "has_changes": bool(added or removed or changed)}
