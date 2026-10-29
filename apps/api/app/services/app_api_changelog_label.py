"""App API Changelog Label — label changelog entries for organization.

Manages changelog labels:
- Define labels with colors
- Assign labels to entries
- Filter entries by label
- Per-installation scoped labels
"""

from __future__ import annotations

from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class ChangelogLabel:
    """A changelog label."""

    label_id: str
    name: str
    color: str = "#808080"


@dataclass
class LabeledEntry:
    """A changelog entry with labels."""

    entry_id: str
    title: str
    labels: list[str] = field(default_factory=list)


class AppAPIChangelogLabel:
    """Label changelog entries for organization."""

    def __init__(self) -> None:
        self._labels: dict[tuple[str, str], ChangelogLabel] = {}
        self._entries: dict[tuple[str, str], LabeledEntry] = {}

    def create_label(
        self, installation_id: str, label_id: str, name: str, color: str = "#808080",
    ) -> ChangelogLabel:
        if not installation_id:
            raise ValueError("installation_id is required")
        label = ChangelogLabel(label_id=label_id, name=name, color=color)
        self._labels[(installation_id, label_id)] = label
        return label

    def label_entry(
        self, installation_id: str, entry_id: str, title: str, label_ids: list[str],
    ) -> LabeledEntry:
        key = (installation_id, entry_id)
        if key not in self._entries:
            self._entries[key] = LabeledEntry(entry_id=entry_id, title=title)
        self._entries[key].labels = list(set(self._entries[key].labels + label_ids))
        return self._entries[key]

    def entries_by_label(self, installation_id: str, label_id: str) -> list[LabeledEntry]:
        return [e for (inst, _), e in self._entries.items() if inst == installation_id and label_id in e.labels]

    def list_labels(self, installation_id: str) -> list[ChangelogLabel]:
        return [l for (inst, _), l in self._labels.items() if inst == installation_id]
