"""App status counter — count apps by status."""

from collections import Counter


def count_by_status(apps: list[dict]) -> dict:
    counts = Counter(a.get("status", "unknown") for a in apps)
    return dict(counts)


def count_by_category(apps: list[dict]) -> dict:
    counts = Counter(a.get("category", "unknown") for a in apps)
    return dict(counts)


def count_by_visibility(apps: list[dict]) -> dict:
    counts = Counter(a.get("visibility", "private") for a in apps)
    return dict(counts)
