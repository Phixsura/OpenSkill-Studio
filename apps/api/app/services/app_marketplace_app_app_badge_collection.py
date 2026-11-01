"""Badge collection — reusable badge/tag component configs."""


BADGE_VARIANTS = {
    "default": "bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300",
    "primary": "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400",
    "success": "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400",
    "warning": "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400",
    "danger": "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
    "info": "bg-cyan-100 text-cyan-700 dark:bg-cyan-900/30 dark:text-cyan-400",
    "purple": "bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400",
}


def build_badge(*, label: str, variant: str = "default", icon: str | None = None,
                  removable: bool = False) -> dict:
    classes = BADGE_VARIANTS.get(variant, BADGE_VARIANTS["default"])
    return {"label": label, "variant": variant, "icon": icon,
            "removable": removable, "classes": classes}


def build_badge_group(*, badges: list[dict]) -> dict:
    return {"badges": [build_badge(**b) for b in badges], "total": len(badges)}
