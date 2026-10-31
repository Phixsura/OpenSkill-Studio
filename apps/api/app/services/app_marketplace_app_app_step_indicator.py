"""Step indicator — progress steps for multi-step flows."""


def build_step_indicator(*, steps: list[str], current_step: int) -> dict:
    if current_step < 0 or current_step >= len(steps):
        current_step = max(0, min(current_step, len(steps) - 1))
    enriched = []
    for i, label in enumerate(steps):
        status = "completed" if i < current_step else "current" if i == current_step else "upcoming"
        enriched.append({"index": i, "label": label, "status": status})
    return {
        "steps": enriched,
        "total": len(steps),
        "current": current_step,
        "progress_pct": round(current_step / max(len(steps) - 1, 1) * 100),
        "is_first": current_step == 0,
        "is_last": current_step == len(steps) - 1,
    }
