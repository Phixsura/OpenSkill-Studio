"""Release pipeline v2 — automated release pipeline with gates and approvals."""


GATE_TYPES = {"manual_approval", "test_pass", "security_scan", "performance_check", "canary_health"}


def create_pipeline_v2(*, app_id: str, version_id: str, gates: list[dict]) -> dict:
    stages = []
    for i, gate in enumerate(gates):
        stages.append({"index": i, "gate_type": gate.get("type", "manual_approval"),
                        "name": gate.get("name", f"Gate {i+1}"), "status": "pending",
                        "required": gate.get("required", True)})
    return {"app_id": app_id, "version_id": version_id, "stages": stages,
            "current_gate": 0, "status": "created", "total_gates": len(stages)}


def pass_gate(*, pipeline: dict, gate_index: int, result: dict) -> dict:
    stages = list(pipeline["stages"])
    if gate_index >= len(stages):
        return {**pipeline, "error": "Invalid gate index"}
    stages[gate_index] = {**stages[gate_index], "status": "passed", "result": result}
    next_gate = gate_index + 1
    all_passed = all(s["status"] == "passed" for s in stages)
    return {**pipeline, "stages": stages, "current_gate": next_gate,
            "status": "completed" if all_passed else "in_progress", "error": None}


def fail_gate(*, pipeline: dict, gate_index: int, reason: str) -> dict:
    stages = list(pipeline["stages"])
    stages[gate_index] = {**stages[gate_index], "status": "failed", "reason": reason}
    required = stages[gate_index].get("required", True)
    return {**pipeline, "stages": stages,
            "status": "blocked" if required else "in_progress"}


def get_pipeline_summary(*, pipeline: dict) -> dict:
    passed = sum(1 for s in pipeline["stages"] if s["status"] == "passed")
    failed = sum(1 for s in pipeline["stages"] if s["status"] == "failed")
    return {"total": len(pipeline["stages"]), "passed": passed, "failed": failed,
            "pending": len(pipeline["stages"]) - passed - failed,
            "progress_pct": round(passed / max(len(pipeline["stages"]), 1) * 100)}
