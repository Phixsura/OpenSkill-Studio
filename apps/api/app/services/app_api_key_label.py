"""App API Key Label — label and organize API keys.

Manages API key labels:
- Add labels/tags to keys
- Group keys by label
- Search keys by label
- Per-installation scoped labels
"""

from __future__ import annotations

from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class LabeledKey:
    """An API key with labels."""

    key_id: str
    name: str
    labels: set[str] = field(default_factory=set)


class AppAPIKeyLabel:
    """Label and organize API keys."""

    def __init__(self) -> None:
        self._keys: dict[tuple[str, str], LabeledKey] = {}

    def register_key(
        self, installation_id: str, key_id: str, name: str,
        labels: list[str] | None = None,
    ) -> LabeledKey:
        if not installation_id:
            raise ValueError("installation_id is required")
        key = (installation_id, key_id)
        if key in self._keys:
            raise ValueError(f"Key {key_id} already registered")
        k = LabeledKey(key_id=key_id, name=name, labels=set(labels or []))
        self._keys[key] = k
        return k

    def add_labels(self, installation_id: str, key_id: str, labels: list[str]) -> LabeledKey:
        k = self._get(installation_id, key_id)
        k.labels.update(labels)
        return k

    def remove_labels(self, installation_id: str, key_id: str, labels: list[str]) -> LabeledKey:
        k = self._get(installation_id, key_id)
        k.labels -= set(labels)
        return k

    def find_by_label(self, installation_id: str, label: str) -> list[LabeledKey]:
        return [k for (inst, _), k in self._keys.items() if inst == installation_id and label in k.labels]

    def all_labels(self, installation_id: str) -> list[str]:
        labels: set[str] = set()
        for (inst, _), k in self._keys.items():
            if inst == installation_id:
                labels.update(k.labels)
        return sorted(labels)

    def list_keys(self, installation_id: str) -> list[LabeledKey]:
        return [k for (inst, _), k in self._keys.items() if inst == installation_id]

    def _get(self, installation_id: str, key_id: str) -> LabeledKey:
        key = (installation_id, key_id)
        k = self._keys.get(key)
        if k is None:
            raise KeyError(f"Key {key_id} not found")
        return k
