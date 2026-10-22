"""Event schema registry — define expected payload shapes for each event type."""

EVENT_SCHEMAS = {
    "submission.completed": {
        "required": ["submission_id", "project_id", "user_id"],
        "optional": ["score", "evaluator_id"],
    },
    "submission.graded": {
        "required": ["submission_id", "grade"],
        "optional": ["feedback", "evaluator_id"],
    },
    "cohort.member_added": {
        "required": ["cohort_id", "user_id"],
        "optional": ["role"],
    },
    "cohort.member_removed": {
        "required": ["cohort_id", "user_id"],
        "optional": ["reason"],
    },
    "project.published": {
        "required": ["project_id"],
        "optional": ["visibility"],
    },
    "app.installed": {
        "required": ["app_id", "org_id", "installed_by"],
        "optional": ["version_id"],
    },
    "app.uninstalled": {
        "required": ["app_id", "org_id"],
        "optional": ["reason"],
    },
}


def get_event_schema(event_type: str) -> dict | None:
    return EVENT_SCHEMAS.get(event_type)


def validate_event_data(event_type: str, data: dict) -> list[str]:
    schema = get_event_schema(event_type)
    if not schema:
        return []
    errors = []
    for field in schema["required"]:
        if field not in data:
            errors.append(f"Missing required field: {field}")
    return errors


def list_event_schemas() -> dict:
    return {k: v for k, v in EVENT_SCHEMAS.items()}
