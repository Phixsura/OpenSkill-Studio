"""Marketplace tags — tag apps for better discovery."""

from collections import defaultdict

_tags: dict[str, set[str]] = defaultdict(set)  # app_id -> tags
_tag_index: dict[str, set[str]] = defaultdict(set)  # tag -> app_ids


def add_tag(app_id: str, tag: str) -> None:
    tag = tag.lower().strip()
    if tag:
        _tags[app_id].add(tag)
        _tag_index[tag].add(app_id)


def remove_tag(app_id: str, tag: str) -> None:
    tag = tag.lower().strip()
    _tags[app_id].discard(tag)
    _tag_index[tag].discard(app_id)


def get_tags(app_id: str) -> list[str]:
    return sorted(_tags.get(app_id, set()))


def find_by_tag(tag: str) -> list[str]:
    return sorted(_tag_index.get(tag.lower().strip(), set()))


def popular_tags(*, limit: int = 20) -> list[dict]:
    counts = [(tag, len(apps)) for tag, apps in _tag_index.items() if apps]
    return [{"tag": t, "count": c} for t, c in sorted(counts, key=lambda x: x[1], reverse=True)[:limit]]
