"""Sparkline — generate sparkline data for inline charts."""


def generate_sparkline(*, values: list[float], label: str = "") -> dict:
    if not values:
        return {"points": [], "label": label, "empty": True}
    min_val = min(values)
    max_val = max(values)
    val_range = max_val - min_val or 1
    normalized = [round((v - min_val) / val_range * 100, 1) for v in values]
    current = values[-1]
    previous = values[-2] if len(values) > 1 else current
    change = round(current - previous, 2)
    change_pct = round(change / max(abs(previous), 0.01) * 100, 1)
    return {
        "points": normalized,
        "raw_values": values,
        "label": label,
        "current": current,
        "min": min_val,
        "max": max_val,
        "change": change,
        "change_pct": change_pct,
        "trend": "up" if change > 0 else "down" if change < 0 else "flat",
        "empty": False,
    }
