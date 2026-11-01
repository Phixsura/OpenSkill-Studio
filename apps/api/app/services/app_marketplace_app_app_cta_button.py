"""CTA button — call-to-action button configurations."""


CTA_STYLES = {
    "primary": {"bg": "bg-blue-600", "text": "text-white", "hover": "hover:bg-blue-700"},
    "secondary": {"bg": "border", "text": "text-gray-700 dark:text-gray-300", "hover": "hover:bg-gray-50"},
    "success": {"bg": "bg-green-600", "text": "text-white", "hover": "hover:bg-green-700"},
    "danger": {"bg": "bg-red-600", "text": "text-white", "hover": "hover:bg-red-700"},
    "ghost": {"bg": "bg-transparent", "text": "text-blue-600", "hover": "hover:bg-blue-50"},
}

CTA_SIZES = {
    "sm": {"px": "px-3", "py": "py-1", "text": "text-xs"},
    "md": {"px": "px-4", "py": "py-2", "text": "text-sm"},
    "lg": {"px": "px-6", "py": "py-3", "text": "text-base"},
    "xl": {"px": "px-8", "py": "py-4", "text": "text-lg"},
}


def build_cta(*, label: str, style: str = "primary", size: str = "md",
                icon: str | None = None, full_width: bool = False) -> dict:
    s = CTA_STYLES.get(style, CTA_STYLES["primary"])
    sz = CTA_SIZES.get(size, CTA_SIZES["md"])
    classes = f"rounded-lg font-semibold {s['bg']} {s['text']} {s['hover']} {sz['px']} {sz['py']} {sz['text']}"
    if full_width:
        classes += " w-full"
    return {"label": label, "style": style, "size": size, "icon": icon,
            "full_width": full_width, "classes": classes}
