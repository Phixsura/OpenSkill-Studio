"""Tag system — tagging and tag-based discovery for marketplace apps."""

from collections import defaultdict

POPULAR_TAGS = ["automation", "integration", "analytics", "webhook", "oauth", "dashboard",
                "notification", "sync", "export", "import", "api", "bot", "scheduler", "monitoring"]


def validate_tags(*, tags: list[str], max_tags: int = 10) -> dict:
    errors = []
    if len(tags) > max_tags:
        errors.append(f"Maximum {max_tags} tags allowed")
    invalid = [t for t in tags if len(t) < 2 or len(t) > 30 or not t.replace("-", "").replace("_", "").isalnum()]
    if invalid:
        errors.append(f"Invalid tags: {', '.join(invalid)}")
    return {"valid": len(errors) == 0, "errors": errors, "tag_count": len(tags)}


def get_trending_tags(*, apps: list[dict], limit: int = 20) -> list[dict]:
    tag_counts = defaultdict(int)
    for app in apps:
        for tag in app.get("tags", []):
            tag_counts[tag] += 1
    return [{"tag": t, "count": c} for t, c in sorted(tag_counts.items(), key=lambda x: -x[1])[:limit]]


def find_apps_by_tag(*, apps: list[dict], tag: str) -> list[dict]:
    return [a for a in apps if tag in a.get("tags", [])]


def suggest_tags(*, description: str) -> list[str]:
    desc_lower = description.lower()
    return [t for t in POPULAR_TAGS if t in desc_lower][:5]
