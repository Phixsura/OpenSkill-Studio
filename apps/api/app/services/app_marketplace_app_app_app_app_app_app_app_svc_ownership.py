"""Service ownership — track who owns and maintains each service."""
from __future__ import annotations


def assign_ownership(services: list[dict]) -> dict:
    by_team: dict[str, list[str]] = {}
    unowned = []
    for s in services:
        team = s.get("team", "")
        if not team:
            unowned.append(s["name"])
        else:
            by_team.setdefault(team, []).append(s["name"])
    return {"by_team": by_team, "teams": sorted(by_team.keys()),
            "unowned": unowned, "unowned_count": len(unowned),
            "total_services": len(services), "all_owned": len(unowned) == 0}


def ownership_matrix(services: list[dict]) -> dict:
    matrix = []
    for s in services:
        matrix.append({"service": s["name"], "team": s.get("team", "unassigned"),
                        "oncall": s.get("oncall", ""), "runbook": s.get("runbook", False),
                        "docs": s.get("docs", False)})
    complete = sum(1 for m in matrix if m["team"] != "unassigned" and m["oncall"] and m["runbook"] and m["docs"])
    return {"matrix": matrix, "total": len(matrix), "complete": complete,
            "completeness_pct": round(complete / max(len(matrix), 1) * 100)}
