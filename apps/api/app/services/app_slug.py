"""App slug utilities — generation, validation, uniqueness check."""

import re
import structlog

log = structlog.get_logger()

SLUG_RE = re.compile(r"^[a-z][a-z0-9-]{0,58}[a-z0-9]$")
RESERVED_SLUGS = frozenset({
    "admin", "api", "app", "apps", "auth", "dashboard", "developer",
    "docs", "help", "install", "login", "marketplace", "oauth",
    "platform", "settings", "signup", "status", "system", "webhook",
})


def validate_slug(slug: str) -> list[str]:
    """Validate an app slug. Returns list of errors (empty = valid)."""
    errors = []
    if not slug:
        errors.append("Slug is required")
        return errors
    if len(slug) < 2:
        errors.append("Slug must be at least 2 characters")
    if len(slug) > 60:
        errors.append("Slug must be at most 60 characters")
    if not SLUG_RE.match(slug):
        errors.append("Slug must be lowercase alphanumeric with hyphens, starting with a letter")
    if "--" in slug:
        errors.append("Slug cannot contain consecutive hyphens")
    if slug in RESERVED_SLUGS:
        errors.append(f"Slug '{slug}' is reserved")
    return errors


def generate_slug(name: str) -> str:
    """Generate a URL-safe slug from an app name."""
    slug = name.lower().strip()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"[\s_]+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    slug = slug.strip("-")
    if not slug or not slug[0].isalpha():
        slug = "app-" + slug
    return slug[:60]


def is_slug_available(slug: str, existing_slugs: set[str]) -> bool:
    """Check if a slug is available (not taken and not reserved)."""
    if slug in RESERVED_SLUGS:
        return False
    return slug not in existing_slugs
