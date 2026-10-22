"""Workflow builder — visual workflow definition for app automation."""


def create_workflow(*, name: str, trigger: dict, actions: list[dict]) -> dict:
    if not trigger:
        return {"error": "Workflow must have a trigger"}
    if not actions:
        return {"error": "Workflow must have at least one action"}
    steps = [{"type": "trigger", "config": trigger}]
    for i, action in enumerate(actions):
        steps.append({"type": "action", "index": i, "config": action})
    return {"name": name, "steps": steps, "step_count": len(steps), "status": "draft", "error": None}


def validate_workflow(*, workflow: dict) -> dict:
    errors = []
    steps = workflow.get("steps", [])
    if not steps:
        errors.append("Workflow has no steps")
    triggers = [s for s in steps if s["type"] == "trigger"]
    if len(triggers) != 1:
        errors.append("Workflow must have exactly one trigger")
    actions = [s for s in steps if s["type"] == "action"]
    if not actions:
        errors.append("Workflow must have at least one action")
    return {"valid": len(errors) == 0, "errors": errors}


def execute_workflow(*, workflow: dict, context: dict) -> dict:
    results = []
    for step in workflow.get("steps", []):
        results.append({"step_type": step["type"], "status": "success", "output": {}})
    return {"workflow": workflow.get("name"), "steps_executed": len(results),
            "all_success": all(r["status"] == "success" for r in results), "results": results}
