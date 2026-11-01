"""On-call scheduler — manage on-call rotations and escalations."""
from __future__ import annotations
import time


def create_rotation(name: str, members: list[str], rotation_days: int = 7) -> dict:
    schedules = []
    for i, member in enumerate(members):
        schedules.append({"member": member, "order": i,
                           "start_offset_days": i * rotation_days})
    return {"name": name, "members": members, "rotation_days": rotation_days,
            "schedules": schedules, "current_index": 0}


def who_is_oncall(rotation: dict, elapsed_days: int = 0) -> dict:
    total = len(rotation["members"])
    if total == 0:
        return {"oncall": None, "error": "no_members"}
    idx = (elapsed_days // rotation["rotation_days"]) % total
    member = rotation["members"][idx]
    days_into = elapsed_days % rotation["rotation_days"]
    return {"oncall": member, "rotation": rotation["name"],
            "days_into_shift": days_into,
            "days_remaining": rotation["rotation_days"] - days_into,
            "next_oncall": rotation["members"][(idx + 1) % total]}


def oncall_summary(rotations: list[dict]) -> dict:
    oncalls = [who_is_oncall(r) for r in rotations]
    return {"rotations": len(rotations), "current_oncalls": oncalls,
            "unique_oncall": len({o["oncall"] for o in oncalls if o.get("oncall")})}
