"""Number formatter — format numbers for display."""


def format_number(*, value: float, style: str = "compact") -> dict:
    if style == "compact":
        if abs(value) >= 1_000_000_000:
            formatted = f"{value / 1_000_000_000:.1f}B"
        elif abs(value) >= 1_000_000:
            formatted = f"{value / 1_000_000:.1f}M"
        elif abs(value) >= 1_000:
            formatted = f"{value / 1_000:.1f}K"
        else:
            formatted = str(int(value)) if value == int(value) else f"{value:.1f}"
    elif style == "currency":
        formatted = f"${value:,.2f}"
    elif style == "percentage":
        formatted = f"{value:.1f}%"
    elif style == "decimal":
        formatted = f"{value:,.2f}"
    else:
        formatted = str(value)
    return {"formatted": formatted, "raw": value, "style": style}


def format_bytes(*, bytes_val: int) -> dict:
    units = [("TB", 1 << 40), ("GB", 1 << 30), ("MB", 1 << 20), ("KB", 1 << 10)]
    for unit, threshold in units:
        if bytes_val >= threshold:
            return {"formatted": f"{bytes_val / threshold:.1f} {unit}", "raw": bytes_val, "unit": unit}
    return {"formatted": f"{bytes_val} B", "raw": bytes_val, "unit": "B"}
