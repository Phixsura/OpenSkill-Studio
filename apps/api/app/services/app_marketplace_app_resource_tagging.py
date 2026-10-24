"""Resource tagging — organize and filter resources with tags."""

import re

TAG_KEY_RE = re.compile(r"^[a-z][a-z0-9_-]{0,31}$")
TAG_VALUE_RE = re.compile(r"^[a-zA-Z0-9_ .-]{0,63}$")


def validate_tags(*, tags: dict[str, str]) -> dict:
    errors = []
    for key, value in tags.items():
        if not TAG_KEY_RE.match(key):
            errors.append(f"Invalid key: '{key}'")
        if not TAG_VALUE_RE.match(value):
            errors.append(f"Invalid value for '{key}': '{value}'")
    if len(tags) > 50:
        errors.append("Maximum 50 tags allowed")
    return {"valid": len(errors) == 0, "errors": errors, "tag_count": len(tags)}


def filter_by_tags(*, resources: list[dict], required_tags: dict[str, str]) -> dict:
    matched = []
    for r in resources:
        tags = r.get("tags", {})
        if all(tags.get(k) == v for k, v in required_tags.items()):
            matched.append(r)
    return {"matched": matched, "total_matched": len(matched),
            "total_resources": len(resources)}


def get_tag_cloud(*, resources: list[dict]) -> dict:
    key_counts: dict[str, dict[str, int]] = {}
    for r in resources:
        for k, v in r.get("tags", {}).items():
            key_counts.setdefault(k, {})
            key_counts[k][v] = key_counts[k].get(v, 0) + 1
    cloud = [{"key": k, "values": [{"value": v, "count": c} for v, c in sorted(vals.items(), key=lambda x: x[1], reverse=True)],
              "total": sum(vals.values())} for k, vals in sorted(key_counts.items())]
    return {"tag_keys": cloud, "unique_keys": len(cloud)}
