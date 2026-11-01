"""Kbd shortcut — keyboard shortcut display helper."""


def format_shortcut(*, keys: list[str], platform: str = "mac") -> dict:
    mac_symbols = {"cmd": "⌘", "shift": "⇧", "alt": "⌥", "ctrl": "⌃", "enter": "↩", "escape": "⎋", "tab": "⇥"}
    win_symbols = {"cmd": "Ctrl", "shift": "Shift", "alt": "Alt", "ctrl": "Ctrl", "enter": "Enter", "escape": "Esc", "tab": "Tab"}
    symbols = mac_symbols if platform == "mac" else win_symbols
    formatted = [symbols.get(k.lower(), k.upper()) for k in keys]
    separator = "" if platform == "mac" else "+"
    return {
        "keys": keys,
        "platform": platform,
        "display": separator.join(formatted),
        "formatted_keys": formatted,
    }
