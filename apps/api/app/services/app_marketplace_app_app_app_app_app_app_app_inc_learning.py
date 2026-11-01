"""Incident learning review — extract learnings from incidents."""
from __future__ import annotations


def extract_learnings(incident: dict) -> dict:
    lessons = []
    if incident.get("detection_time_min", 0) > 30:
        lessons.append({"area": "detection", "lesson": "Improve monitoring to detect issues faster",
                          "priority": "high"})
    if incident.get("resolution_time_min", 0) > 120:
        lessons.append({"area": "response", "lesson": "Create runbook for faster resolution",
                          "priority": "high"})
    if not incident.get("had_runbook", False):
        lessons.append({"area": "documentation", "lesson": "Create runbook for this failure mode",
                          "priority": "medium"})
    if incident.get("affected_customers", 0) > 100:
        lessons.append({"area": "communication", "lesson": "Improve customer notification process",
                          "priority": "medium"})
    return {"incident_id": incident.get("id", ""), "lessons": lessons,
            "lesson_count": len(lessons), "action_items": len(lessons)}


def learning_trends(reviews: list[dict]) -> dict:
    by_area: dict[str, int] = {}
    for r in reviews:
        for l in r.get("lessons", []):
            by_area[l["area"]] = by_area.get(l["area"], 0) + 1
    top_area = max(by_area, key=by_area.get) if by_area else None
    return {"total_reviews": len(reviews),
            "total_lessons": sum(by_area.values()),
            "by_area": by_area, "top_area": top_area}
