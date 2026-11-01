"""Number formatter — human-friendly number formatting for marketplace stats."""


def format_compact(*, value: int) -> str:
    if value >= 1_000_000:
        return f"{value / 1_000_000:.1f}M"
    if value >= 1_000:
        return f"{value / 1_000:.1f}K"
    return str(value)


def format_currency(*, cents: int, currency: str = "USD") -> str:
    symbols = {"USD": "$", "EUR": "€", "GBP": "£", "JPY": "¥"}
    symbol = symbols.get(currency, "$")
    if currency == "JPY":
        return f"{symbol}{cents:,}"
    return f"{symbol}{cents / 100:,.2f}"


def format_percentage(*, value: float, decimals: int = 1) -> str:
    return f"{value:.{decimals}f}%"


def format_bytes(*, bytes_val: int) -> str:
    if bytes_val >= 1_073_741_824:
        return f"{bytes_val / 1_073_741_824:.1f} GB"
    if bytes_val >= 1_048_576:
        return f"{bytes_val / 1_048_576:.1f} MB"
    if bytes_val >= 1024:
        return f"{bytes_val / 1024:.1f} KB"
    return f"{bytes_val} B"


def format_duration(*, seconds: int) -> str:
    if seconds >= 86400:
        days = seconds // 86400
        return f"{days}d {(seconds % 86400) // 3600}h"
    if seconds >= 3600:
        return f"{seconds // 3600}h {(seconds % 3600) // 60}m"
    if seconds >= 60:
        return f"{seconds // 60}m {seconds % 60}s"
    return f"{seconds}s"
