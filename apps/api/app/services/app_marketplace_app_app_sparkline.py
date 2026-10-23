"""Sparkline — inline mini chart data generator."""


def build_sparkline(*, data: list[float], label: str = "") -> dict:
    if not data:
        return {"points": [], "label": label, "min": 0, "max": 0, "current": 0, "trend": "flat"}
    lo, hi = min(data), max(data)
    span = hi - lo if hi != lo else 1.0
    normalized = [round((v - lo) / span * 100, 1) for v in data]
    current = data[-1]
    prev = data[-2] if len(data) >= 2 else current
    trend = "up" if current > prev else "down" if current < prev else "flat"
    return {"points": normalized, "raw": data, "label": label,
            "min": lo, "max": hi, "current": current,
            "trend": trend, "point_count": len(data)}
