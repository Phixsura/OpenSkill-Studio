"""App Changelog Label — categorize and label changelog entries.

Manages labels for changelog entries:
- Define label taxonomy (type, scope, impact)
- Apply labels to entries
- Query entries by label
- Label statistics
"""

from __future__ import annotations

from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class Label:
    """A changelog label."""

    label_id: str
    name: str
    category: str  # "type", "scope", "impact"
    color: str = "#6b7280"


@dataclass
class LabeledEntry:
    """A changelog entry with labels."""

    entry_id: str
    version: str
    title: str
    labels: list[str] = field(default_factory=list)


class AppChangelogLabel:
    """Categorize and label changelog entries."""

    def __init__(self) -> None:
        # (installation_id, label_id) → Label
        self._labels: dict[tuple[str, str], Label] = {}
        # (installation_id, entry_id) → LabeledEntry
        self._entries: dict[tuple[str, str], LabeledEntry] = {}

    def define_label(
        self,
        installation_id: str,
        label_id: str,
        name: str,
        category: str,
        color: str = "#6b7280",
    ) -> Label:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not label_id:
            raise ValueError("label_id is required")
        if category not in ("type", "scope", "impact"):
            raise ValueError("category must be type, scope, or impact")

        key = (installation_id, label_id)
        if key in self._labels:
            raise ValueError(f"Label {label_id} already exists")

        label = Label(label_id=label_id, name=name, category=category, color=color)
        self._labels[key] = label
        return label

    def add_entry(
        self,
        installation_id: str,
        entry_id: str,
        version: str,
        title: str,
        labels: list[str] | None = None,
    ) -> LabeledEntry:
        if not entry_id:
            raise ValueError("entry_id is required")

        key = (installation_id, entry_id)
        entry = LabeledEntry(
            entry_id=entry_id, version=version,
            title=title, labels=labels or [],
        )
        self._entries[key] = entry
        return entry

    def apply_label(
        self, installation_id: str, entry_id: str, label_id: str
    ) -> LabeledEntry:
        entry = self._get_entry(installation_id, entry_id)
        if (installation_id, label_id) not in self._labels:
            raise KeyError(f"Label {label_id} not found")
        if label_id not in entry.labels:
            entry.labels.append(label_id)
        return entry

    def remove_label(
        self, installation_id: str, entry_id: str, label_id: str
    ) -> LabeledEntry:
        entry = self._get_entry(installation_id, entry_id)
        entry.labels = [l for l in entry.labels if l != label_id]
        return entry

    def find_by_label(
        self, installation_id: str, label_id: str
    ) -> list[LabeledEntry]:
        return [
            e for (inst, _), e in self._entries.items()
            if inst == installation_id and label_id in e.labels
        ]

    def get_label_stats(self, installation_id: str) -> dict[str, int]:
        """Count entries per label."""
        counts: dict[str, int] = {}
        for (inst, _), entry in self._entries.items():
            if inst != installation_id:
                continue
            for lid in entry.labels:
                counts[lid] = counts.get(lid, 0) + 1
        return counts

    def list_labels(self, installation_id: str, category: str | None = None) -> list[Label]:
        labels = [l for (inst, _), l in self._labels.items() if inst == installation_id]
        if category:
            labels = [l for l in labels if l.category == category]
        return labels

    def _get_entry(self, installation_id: str, entry_id: str) -> LabeledEntry:
        key = (installation_id, entry_id)
        entry = self._entries.get(key)
        if entry is None:
            raise KeyError(f"Entry {entry_id} not found")
        return entry
