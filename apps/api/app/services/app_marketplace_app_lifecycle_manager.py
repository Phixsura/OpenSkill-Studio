"""Lifecycle manager — orchestrate the complete app lifecycle from creation to sunset."""

LIFECYCLE_STAGES = ["draft", "development", "review", "published", "maintenance", "deprecated", "sunset"]


def get_lifecycle_stage(*, app: dict) -> dict:
    status = app.get("status", "draft")
    stage_map = {"draft": "draft", "in_review": "review", "published": "published",
                  "deprecated": "deprecated", "suspended": "maintenance", "archived": "sunset"}
    stage = stage_map.get(status, "draft")
    idx = LIFECYCLE_STAGES.index(stage) if stage in LIFECYCLE_STAGES else 0
    return {"stage": stage, "stage_index": idx, "total_stages": len(LIFECYCLE_STAGES),
            "progress_pct": round(idx / (len(LIFECYCLE_STAGES) - 1) * 100)}


def get_allowed_transitions(*, current_stage: str) -> list[str]:
    transitions = {
        "draft": ["development"], "development": ["review"], "review": ["published", "development"],
        "published": ["maintenance", "deprecated"], "maintenance": ["published", "deprecated"],
        "deprecated": ["sunset"], "sunset": [],
    }
    return transitions.get(current_stage, [])


def transition_app(*, app: dict, target_stage: str) -> dict:
    current = get_lifecycle_stage(app=app)["stage"]
    allowed = get_allowed_transitions(current_stage=current)
    if target_stage not in allowed:
        return {"error": f"Cannot transition from {current} to {target_stage}"}
    return {"previous_stage": current, "new_stage": target_stage, "error": None}
