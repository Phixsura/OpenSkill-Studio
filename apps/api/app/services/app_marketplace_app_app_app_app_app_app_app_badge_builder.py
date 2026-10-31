"""Badge builder — create consistent badge/chip components for the UI."""
from __future__ import annotations

VARIANTS = {
    "default": {"bg": "bg-gray-100", "text": "text-gray-700", "dark_bg": "dark:bg-gray-800", "dark_text": "dark:text-gray-300"},
    "primary": {"bg": "bg-blue-100", "text": "text-blue-700", "dark_bg": "dark:bg-blue-900/20", "dark_text": "dark:text-blue-400"},
    "success": {"bg": "bg-green-100", "text": "text-green-700", "dark_bg": "dark:bg-green-900/20", "dark_text": "dark:text-green-400"},
    "warning": {"bg": "bg-yellow-100", "text": "text-yellow-700", "dark_bg": "dark:bg-yellow-900/20", "dark_text": "dark:text-yellow-400"},
    "danger": {"bg": "bg-red-100", "text": "text-red-700", "dark_bg": "dark:bg-red-900/20", "dark_text": "dark:text-red-400"},
    "info": {"bg": "bg-purple-100", "text": "text-purple-700", "dark_bg": "dark:bg-purple-900/20", "dark_text": "dark:text-purple-400"},
}


def build_badge(*, label: str, variant: str = "default", size: str = "sm",
                  icon: str = "", dot: bool = False) -> dict:
    v = VARIANTS.get(variant, VARIANTS["default"])
    classes = f"{v['bg']} {v['text']} {v['dark_bg']} {v['dark_text']}"
    size_class = "text-xs px-2 py-0.5" if size == "sm" else "text-sm px-3 py-1"
    return {"label": label, "variant": variant, "classes": f"{classes} {size_class} rounded-full",
            "icon": icon, "dot": dot}


def build_status_badge(status: str) -> dict:
    mapping = {"active": "success", "inactive": "default", "pending": "warning",
               "error": "danger", "beta": "info", "new": "primary"}
    return build_badge(label=status.capitalize(), variant=mapping.get(status, "default"), dot=True)
