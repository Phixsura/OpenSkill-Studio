"""Theme token — design token system for consistent theming."""


TOKENS = {
    "light": {
        "bg-primary": "#ffffff", "bg-secondary": "#f9fafb", "bg-tertiary": "#f3f4f6",
        "text-primary": "#111827", "text-secondary": "#6b7280", "text-muted": "#9ca3af",
        "border": "#e5e7eb", "accent": "#3b82f6", "success": "#22c55e",
        "warning": "#f59e0b", "error": "#ef4444",
    },
    "dark": {
        "bg-primary": "#0a0a0a", "bg-secondary": "#171717", "bg-tertiary": "#262626",
        "text-primary": "#fafafa", "text-secondary": "#a3a3a3", "text-muted": "#737373",
        "border": "#404040", "accent": "#60a5fa", "success": "#4ade80",
        "warning": "#fbbf24", "error": "#f87171",
    },
}


def get_tokens(*, theme: str = "light") -> dict:
    tokens = TOKENS.get(theme, TOKENS["light"])
    return {"theme": theme, "tokens": tokens, "token_count": len(tokens)}


def generate_css_vars(*, theme: str = "light") -> dict:
    tokens = TOKENS.get(theme, TOKENS["light"])
    css = ":root {\n" + "\n".join(f"  --{k}: {v};" for k, v in tokens.items()) + "\n}"
    return {"css": css, "theme": theme}
