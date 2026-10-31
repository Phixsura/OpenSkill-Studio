"""Extension Tagging — manage tags and taxonomies for marketplace extensions.

Provides tag CRUD, auto-suggest, tag popularity tracking, and
tag-based discovery for the extension marketplace.
"""
from __future__ import annotations
from collections import defaultdict
from dataclasses import dataclass


@dataclass
class Tag:
    name: str
    slug: str
    category: str = ""
    usage_count: int = 0
    approved: bool = True


class TaggingService:
    """Manages tags for extension discovery and categorization."""

    def __init__(self):
        self._tags: dict[str, Tag] = {}
        self._extension_tags: dict[str, set[str]] = defaultdict(set)  # ext -> {slugs}
        self._tag_extensions: dict[str, set[str]] = defaultdict(set)  # slug -> {exts}

    def create_tag(self, name: str, category: str = "") -> Tag:
        slug = name.lower().replace(" ", "-").replace("_", "-")
        if slug in self._tags:
            return self._tags[slug]
        tag = Tag(name=name, slug=slug, category=category)
        self._tags[slug] = tag
        return tag

    def add_tag(self, extension_id: str, tag_slug: str) -> bool:
        if tag_slug not in self._tags:
            return False
        if tag_slug not in self._extension_tags[extension_id]:
            self._extension_tags[extension_id].add(tag_slug)
            self._tag_extensions[tag_slug].add(extension_id)
            self._tags[tag_slug].usage_count += 1
        return True

    def remove_tag(self, extension_id: str, tag_slug: str) -> bool:
        if tag_slug in self._extension_tags.get(extension_id, set()):
            self._extension_tags[extension_id].discard(tag_slug)
            self._tag_extensions[tag_slug].discard(extension_id)
            self._tags[tag_slug].usage_count = max(0, self._tags[tag_slug].usage_count - 1)
            return True
        return False

    def get_extension_tags(self, extension_id: str) -> list[Tag]:
        slugs = self._extension_tags.get(extension_id, set())
        return sorted([self._tags[s] for s in slugs if s in self._tags], key=lambda t: t.name)

    def get_extensions_by_tag(self, tag_slug: str) -> list[str]:
        return sorted(self._tag_extensions.get(tag_slug, set()))

    def suggest(self, prefix: str, limit: int = 10) -> list[Tag]:
        p = prefix.lower()
        matches = [t for t in self._tags.values() if t.slug.startswith(p) and t.approved]
        return sorted(matches, key=lambda t: t.usage_count, reverse=True)[:limit]

    def get_popular(self, limit: int = 20) -> list[Tag]:
        return sorted(self._tags.values(), key=lambda t: t.usage_count, reverse=True)[:limit]

    def get_related(self, tag_slug: str, limit: int = 10) -> list[Tag]:
        """Find tags commonly used with the given tag."""
        co_tags: dict[str, int] = defaultdict(int)
        for ext_id in self._tag_extensions.get(tag_slug, set()):
            for other in self._extension_tags.get(ext_id, set()):
                if other != tag_slug:
                    co_tags[other] += 1
        return sorted(
            [self._tags[s] for s in sorted(co_tags, key=co_tags.get, reverse=True) if s in self._tags],
            key=lambda t: t.usage_count, reverse=True,
        )[:limit]

    def search_tags(self, query: str) -> list[Tag]:
        q = query.lower()
        return [t for t in self._tags.values() if q in t.slug or q in t.name.lower()]
