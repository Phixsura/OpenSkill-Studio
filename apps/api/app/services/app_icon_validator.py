"""App icon URL validator."""

from urllib.parse import urlparse

ALLOWED_EXTENSIONS = frozenset({".png", ".jpg", ".jpeg", ".svg", ".webp"})
MAX_ICON_URL_LENGTH = 500

def validate_icon_url(url: str | None) -> list[str]:
    if not url: return []
    errors = []
    if len(url) > MAX_ICON_URL_LENGTH:
        errors.append(f"Icon URL too long (max {MAX_ICON_URL_LENGTH})")
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            errors.append("Icon URL must be HTTP(S)")
        path = parsed.path.lower()
        if not any(path.endswith(ext) for ext in ALLOWED_EXTENSIONS):
            errors.append(f"Icon must be an image ({', '.join(sorted(ALLOWED_EXTENSIONS))})")
    except Exception:
        errors.append("Invalid icon URL")
    return errors
