"""Alert banner — dismissible alert banners for important messages."""


ALERT_VARIANTS = {
    "info": {"icon": "ℹ️", "bg": "bg-blue-50 border-blue-200 dark:bg-blue-900/10 dark:border-blue-800"},
    "success": {"icon": "✅", "bg": "bg-green-50 border-green-200 dark:bg-green-900/10 dark:border-green-800"},
    "warning": {"icon": "⚠️", "bg": "bg-yellow-50 border-yellow-200 dark:bg-yellow-900/10 dark:border-yellow-800"},
    "error": {"icon": "❌", "bg": "bg-red-50 border-red-200 dark:bg-red-900/10 dark:border-red-800"},
}


def build_alert(*, message: str, variant: str = "info", title: str | None = None,
                  dismissible: bool = True, action: dict | None = None) -> dict:
    v = ALERT_VARIANTS.get(variant, ALERT_VARIANTS["info"])
    return {
        "message": message,
        "title": title,
        "variant": variant,
        "icon": v["icon"],
        "bg_class": v["bg"],
        "dismissible": dismissible,
        "action": action,
    }
