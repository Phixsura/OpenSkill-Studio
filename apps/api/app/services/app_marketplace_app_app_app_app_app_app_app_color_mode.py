"""Color mode manager — system/light/dark theme preference handler."""
from __future__ import annotations

MODES = {
    "light": {"label": "Light", "icon": "☀️", "bg": "#FFFFFF", "fg": "#1F2937"},
    "dark": {"label": "Dark", "icon": "🌙", "bg": "#111827", "fg": "#F9FAFB"},
    "system": {"label": "System", "icon": "💻", "bg": None, "fg": None},
}


def get_mode(mode: str) -> dict:
    m = MODES.get(mode, MODES["system"])
    return {"mode": mode, **m}


def resolve_mode(preference: str, *, system_dark: bool = False) -> dict:
    if preference == "system":
        resolved = "dark" if system_dark else "light"
    else:
        resolved = preference if preference in ("light", "dark") else "light"
    return {"preference": preference, "resolved": resolved, **MODES.get(resolved, MODES["light"])}


def list_modes() -> list[dict]:
    return [{"id": k, **v} for k, v in MODES.items()]
