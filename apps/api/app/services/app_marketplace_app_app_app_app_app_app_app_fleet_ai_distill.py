"""Fleet AI Distillation — track knowledge distillation from large to small models."""
from __future__ import annotations
def fleet_ai_distillation(jobs: list[dict]) -> dict:
    active = [j for j in jobs if j.get("active", True)]
    teacher_params = sum(j.get("teacher_params_b", 0) for j in jobs)
    student_params = sum(j.get("student_params_b", 0) for j in jobs)
    retention = round(sum(j.get("retention_pct", 0) for j in jobs) / max(len(jobs), 1), 1)
    return {"jobs": len(jobs), "active": len(active), "teacher_params_b": teacher_params,
            "student_params_b": student_params, "retention_pct": retention, "successful": retention > 90}
