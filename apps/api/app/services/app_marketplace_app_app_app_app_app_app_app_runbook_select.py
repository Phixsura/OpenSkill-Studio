"""Incident runbook selector — auto-select runbook based on incident type."""
from __future__ import annotations


def select_runbook(incident: dict, runbooks: list[dict]) -> dict:
    matches = []
    for rb in runbooks:
        score = 0
        if incident.get("service") in rb.get("services", []):
            score += 3
        if incident.get("type") in rb.get("incident_types", []):
            score += 5
        if incident.get("severity") in rb.get("severities", []):
            score += 2
        for tag in incident.get("tags", []):
            if tag in rb.get("tags", []):
                score += 1
        if score > 0:
            matches.append({"runbook": rb["name"], "score": score,
                            "steps": rb.get("steps", 0)})
    matches.sort(key=lambda m: -m["score"])
    best = matches[0] if matches else None
    return {"selected": best["runbook"] if best else None,
            "confidence": best["score"] if best else 0,
            "alternatives": matches[1:3] if len(matches) > 1 else [],
            "total_matches": len(matches)}
