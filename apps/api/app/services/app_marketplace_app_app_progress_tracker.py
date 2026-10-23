"""Progress tracker — multi-step process progress display."""

import html


def build_progress(*, steps: list[dict], current_step: int = 0) -> dict:
    items = []
    for i, s in enumerate(steps):
        status = "completed" if i < current_step else "current" if i == current_step else "pending"
        items.append({
            "index": i,
            "label": html.escape(s.get("label", f"Step {i+1}")),
            "description": html.escape(s.get("description", "")),
            "status": status,
            "icon": "✓" if status == "completed" else str(i + 1),
        })
    pct = round(current_step / max(len(items) - 1, 1) * 100) if len(items) > 1 else (100 if current_step > 0 else 0)
    return {"steps": items, "total": len(items), "current": current_step,
            "progress_pct": pct, "is_complete": current_step >= len(items) - 1}
