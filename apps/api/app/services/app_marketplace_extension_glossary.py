"""Platform Glossary — searchable glossary of platform terminology.

Defines and searches platform terms with categories, related terms,
and contextual examples for developer documentation.
"""
from __future__ import annotations
from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class GlossaryTerm:
    term: str
    definition: str
    category: str
    related: list[str] = field(default_factory=list)
    example: str = ""


class PlatformGlossaryService:
    """Searchable glossary of platform terminology."""

    def __init__(self):
        self._terms: dict[str, GlossaryTerm] = {}

    def add_term(self, term: str, definition: str, category: str,
                 related: list[str] | None = None, example: str = "") -> GlossaryTerm:
        gt = GlossaryTerm(term=term, definition=definition, category=category,
                          related=related or [], example=example)
        self._terms[term.lower()] = gt
        return gt

    def lookup(self, term: str) -> GlossaryTerm | None:
        return self._terms.get(term.lower())

    def search(self, query: str) -> list[GlossaryTerm]:
        q = query.lower()
        return [t for t in self._terms.values()
                if q in t.term.lower() or q in t.definition.lower()]

    def get_by_category(self, category: str) -> list[GlossaryTerm]:
        return sorted([t for t in self._terms.values() if t.category == category],
                      key=lambda t: t.term)

    def get_categories(self) -> list[str]:
        return sorted({t.category for t in self._terms.values()})

    def get_all(self) -> list[GlossaryTerm]:
        return sorted(self._terms.values(), key=lambda t: t.term)

    def get_related(self, term: str) -> list[GlossaryTerm]:
        gt = self._terms.get(term.lower())
        if not gt:
            return []
        return [self._terms[r.lower()] for r in gt.related if r.lower() in self._terms]
