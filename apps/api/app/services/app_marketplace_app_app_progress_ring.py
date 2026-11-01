"""Progress ring — circular progress indicator data."""


def calculate_ring(*, value: float, max_value: float = 100, label: str = "") -> dict:
    pct = round(min(value / max(max_value, 0.01) * 100, 100), 1)
    circumference = 2 * 3.14159 * 45  # radius 45
    offset = round(circumference * (1 - pct / 100), 1)
    color = "green" if pct >= 80 else "blue" if pct >= 50 else "yellow" if pct >= 25 else "red"
    return {
        "value": value,
        "max_value": max_value,
        "percentage": pct,
        "label": label,
        "circumference": round(circumference, 1),
        "offset": offset,
        "color": color,
    }
