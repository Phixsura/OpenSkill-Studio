"""Progress tracker — track multi-step process completion."""


def create_progress(*, title: str, steps: list[dict]) -> dict:
    enriched = []
    for i, step in enumerate(steps):
        enriched.append({
            "index": i,
            "name": step["name"],
            "status": step.get("status", "pending"),
            "description": step.get("description", ""),
        })
    completed = sum(1 for s in enriched if s["status"] == "completed")
    current = next((s["index"] for s in enriched if s["status"] == "in_progress"), None)
    return {
        "title": title,
        "steps": enriched,
        "total_steps": len(enriched),
        "completed_steps": completed,
        "current_step": current,
        "progress_pct": round(completed / max(len(enriched), 1) * 100),
        "all_complete": completed == len(enriched),
    }
