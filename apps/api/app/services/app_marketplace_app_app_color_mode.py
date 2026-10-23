"""Color mode — manage theme preference and color mode switching."""


MODES = {
    "light": {"label": "Light", "icon": "☀️", "bg": "#ffffff", "text": "#1a1a1a"},
    "dark": {"label": "Dark", "icon": "🌙", "bg": "#0a0a0a", "text": "#fafafa"},
    "system": {"label": "System", "icon": "💻", "bg": None, "text": None},
}


def get_color_mode(*, preference: str = "system", system_preference: str = "light") -> dict:
    mode = MODES.get(preference, MODES["system"])
    effective = preference if preference != "system" else system_preference
    effective_mode = MODES.get(effective, MODES["light"])
    return {
        "preference": preference,
        "effective": effective,
        "mode_info": mode,
        "effective_bg": effective_mode["bg"],
        "effective_text": effective_mode["text"],
        "available_modes": list(MODES.keys()),
    }
