"""Step wizard — multi-step form wizard with validation."""

import html


def build_step_wizard(*, steps: list[dict], current_step: int = 0) -> dict:
    items = []
    for i, s in enumerate(steps):
        status = "completed" if i < current_step else "current" if i == current_step else "upcoming"
        items.append({
            "index": i,
            "title": html.escape(s.get("title", f"Step {i+1}")),
            "description": html.escape(s.get("description", "")),
            "icon": s.get("icon", str(i + 1)),
            "status": status,
            "optional": s.get("optional", False),
        })
    return {"steps": items, "current": current_step, "total": len(items),
            "progress_pct": round(current_step / max(len(items), 1) * 100),
            "can_go_back": current_step > 0,
            "can_go_next": current_step < len(items) - 1,
            "is_final": current_step == len(items) - 1}
