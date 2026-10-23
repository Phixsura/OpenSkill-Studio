"""Number formatter — format numbers for display with compact and currency modes."""
from __future__ import annotations


def format_compact(n: float) -> str:
    if abs(n) >= 1_000_000_000:
        return f"{n / 1_000_000_000:.1f}B"
    if abs(n) >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if abs(n) >= 1_000:
        return f"{n / 1_000:.1f}K"
    return str(int(n)) if n == int(n) else f"{n:.1f}"


def format_currency(amount: float, *, currency: str = "USD") -> str:
    symbols = {"USD": "$", "EUR": "€", "GBP": "£", "JPY": "¥"}
    symbol = symbols.get(currency, currency + " ")
    if abs(amount) >= 1_000_000:
        return f"{symbol}{amount / 1_000_000:.1f}M"
    if abs(amount) >= 1_000:
        return f"{symbol}{amount:,.0f}"
    return f"{symbol}{amount:.2f}"


def format_percentage(value: float, *, decimals: int = 1) -> str:
    return f"{value:.{decimals}f}%"


def format_bytes(b: int) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if abs(b) < 1024:
            return f"{b:.1f} {unit}" if b != int(b) else f"{b} {unit}"
        b /= 1024
    return f"{b:.1f} PB"
