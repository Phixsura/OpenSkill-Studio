"""Deployment pipeline validator — validate pipeline configs before execution."""
from __future__ import annotations


def validate_pipeline(config: dict) -> dict:
    errors = []
    stages = config.get("stages", [])
    if not stages:
        errors.append({"field": "stages", "error": "at_least_one_stage_required"})
    stage_names = set()
    for i, stage in enumerate(stages):
        if "name" not in stage:
            errors.append({"field": f"stages[{i}].name", "error": "required"})
        elif stage["name"] in stage_names:
            errors.append({"field": f"stages[{i}].name", "error": "duplicate_name"})
        else:
            stage_names.add(stage["name"])
        if "action" not in stage:
            errors.append({"field": f"stages[{i}].action", "error": "required"})
    if config.get("trigger") not in ("push", "manual", "schedule", None):
        errors.append({"field": "trigger", "error": "invalid_trigger_type"})
    return {"valid": len(errors) == 0, "errors": errors, "stages": len(stages)}


def pipeline_summary(configs: list[dict]) -> dict:
    results = [validate_pipeline(c) for c in configs]
    valid = sum(1 for r in results if r["valid"])
    return {"total": len(configs), "valid": valid, "invalid": len(configs) - valid}
