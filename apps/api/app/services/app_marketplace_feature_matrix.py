"""Feature Matrix — generate feature comparison matrices for extensions.

Compares feature sets across extensions in a category to help users
choose the right extension for their needs.
"""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class ExtensionFeatures:
    extension_id: str
    name: str
    features: dict[str, bool | str | int]  # feature_key -> value


class FeatureMatrixBuilder:
    """Builds feature comparison matrices for marketplace categories."""

    def __init__(self):
        self._extensions: dict[str, ExtensionFeatures] = {}
        self._feature_labels: dict[str, str] = {}
        self._feature_groups: dict[str, list[str]] = {}  # group -> [feature_keys]

    def register_extension(self, ext: ExtensionFeatures) -> None:
        self._extensions[ext.extension_id] = ext

    def define_feature(self, key: str, label: str, group: str = "General") -> None:
        self._feature_labels[key] = label
        self._feature_groups.setdefault(group, [])
        if key not in self._feature_groups[group]:
            self._feature_groups[group].append(key)

    def build_matrix(self, extension_ids: list[str] | None = None) -> dict:
        """Build a complete feature comparison matrix."""
        exts = [self._extensions[eid] for eid in (extension_ids or self._extensions.keys())
                if eid in self._extensions]
        if not exts:
            return {"extensions": [], "groups": [], "matrix": {}}

        groups = []
        for group_name, feature_keys in self._feature_groups.items():
            group_data = {"name": group_name, "features": []}
            for key in feature_keys:
                label = self._feature_labels.get(key, key)
                values = {}
                for ext in exts:
                    val = ext.features.get(key)
                    values[ext.extension_id] = {"value": val, "has": val is not None and val is not False}
                group_data["features"].append({"key": key, "label": label, "values": values})
            groups.append(group_data)

        return {
            "extensions": [{"id": e.extension_id, "name": e.name} for e in exts],
            "groups": groups,
        }

    def get_unique_features(self, extension_id: str) -> list[str]:
        """Get features unique to this extension (no other has them)."""
        ext = self._extensions.get(extension_id)
        if not ext:
            return []
        others = [e for e in self._extensions.values() if e.extension_id != extension_id]
        unique = []
        for key, val in ext.features.items():
            if val and not any(o.features.get(key) for o in others):
                unique.append(key)
        return sorted(unique)

    def get_missing_features(self, extension_id: str) -> list[str]:
        """Get features this extension lacks but others have."""
        ext = self._extensions.get(extension_id)
        if not ext:
            return []
        all_features = set()
        for e in self._extensions.values():
            for k, v in e.features.items():
                if v:
                    all_features.add(k)
        return sorted(k for k in all_features if not ext.features.get(k))

    def get_feature_coverage(self, extension_id: str) -> float:
        """Percentage of defined features this extension supports."""
        ext = self._extensions.get(extension_id)
        if not ext:
            return 0.0
        total = len(self._feature_labels)
        if total == 0:
            return 100.0
        has = sum(1 for k in self._feature_labels if ext.features.get(k))
        return round(has / total * 100, 1)
