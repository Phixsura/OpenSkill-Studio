"""Truncated text — smart text truncation for UI display."""

import html


def truncate_text(*, text: str, max_length: int = 100, suffix: str = "...") -> dict:
    safe = html.escape(text)
    if len(safe) <= max_length:
        return {"text": safe, "truncated": False, "full_length": len(safe)}
    cutoff = max_length - len(suffix)
    # Try to break at word boundary
    space_pos = safe.rfind(" ", 0, cutoff)
    if space_pos > cutoff * 0.5:
        truncated = safe[:space_pos] + suffix
    else:
        truncated = safe[:cutoff] + suffix
    return {"text": truncated, "truncated": True, "full_length": len(safe),
            "display_length": len(truncated)}


def truncate_middle(*, text: str, max_length: int = 40) -> dict:
    if len(text) <= max_length:
        return {"text": text, "truncated": False}
    keep = (max_length - 3) // 2
    return {"text": f"{text[:keep]}...{text[-keep:]}", "truncated": True}
