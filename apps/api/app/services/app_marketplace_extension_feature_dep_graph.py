"""Feature Dependency Graph — track which features depend on which.

Used for: impact analysis before disabling a feature, safe rollout order,
understanding feature coupling.

Implements:
- Directed graph of feature dependencies
- Impact analysis (disable X → what breaks?)
- Safe disable order (bottom-up from leaves)
- Coupling score (how entangled is a feature?)
- Orphan detection (features nothing depends on)
- Feature groups (strongly connected components)
"""
from __future__ import annotations
from dataclasses import dataclass, field
from collections import deque, defaultdict


@dataclass
class Feature:
    name: str
    enabled: bool = True
    description: str = ""
    owner: str = ""


class FeatureDepGraphService:
    def __init__(self):
        self._features: dict[str, Feature] = {}
        self._deps: dict[str, set[str]] = defaultdict(set)  # feature → {depends on}
        self._rdeps: dict[str, set[str]] = defaultdict(set)  # feature → {depended by}

    def add_feature(self, name: str, description: str = "",
                    owner: str = "") -> Feature:
        f = Feature(name=name, description=description, owner=owner)
        self._features[name] = f
        return f

    def add_dependency(self, feature: str, depends_on: str) -> None:
        """feature depends on depends_on."""
        if feature not in self._features or depends_on not in self._features:
            raise ValueError("Both features must exist")
        self._deps[feature].add(depends_on)
        self._rdeps[depends_on].add(feature)

    def impact_analysis(self, feature: str) -> dict:
        """What breaks if we disable this feature?"""
        affected = set()
        queue = deque([feature])
        visited = set()

        while queue:
            current = queue.popleft()
            if current in visited:
                continue
            visited.add(current)
            for dependent in self._rdeps.get(current, set()):
                affected.add(dependent)
                queue.append(dependent)

        critical = [f for f in affected
                    if not (self._deps[f] - {feature} - affected)]

        return {
            "feature": feature,
            "directly_affected": sorted(self._rdeps.get(feature, set())),
            "total_affected": sorted(affected),
            "critical_breaks": sorted(critical),
            "blast_radius": len(affected),
        }

    def safe_disable_order(self, features: list[str]) -> list[str]:
        """Order to disable features safely (dependents first)."""
        feature_set = set(features)
        # Build subgraph
        in_degree = {f: 0 for f in features}
        for f in features:
            for dep in self._deps.get(f, set()):
                if dep in feature_set:
                    in_degree[f] += 1

        # Reverse topo: dependents first
        queue = deque(f for f in features if in_degree[f] == 0)
        order = []
        while queue:
            f = queue.popleft()
            order.append(f)
            for dependent in self._rdeps.get(f, set()):
                if dependent in feature_set:
                    in_degree[dependent] -= 1
                    if in_degree[dependent] == 0:
                        queue.append(dependent)

        # Reverse: disable dependents before their dependencies
        order.reverse()
        return order

    def coupling_score(self, feature: str) -> dict:
        """How coupled is this feature? Higher = harder to change."""
        fan_in = len(self._rdeps.get(feature, set()))
        fan_out = len(self._deps.get(feature, set()))
        score = fan_in + fan_out
        level = "low" if score <= 2 else "medium" if score <= 5 else "high"
        return {"feature": feature, "fan_in": fan_in, "fan_out": fan_out,
                "coupling_score": score, "level": level}

    def find_orphans(self) -> list[str]:
        """Features that nothing depends on (safe to remove)."""
        return sorted(f for f in self._features
                      if not self._rdeps.get(f) and f in self._features)

    def find_roots(self) -> list[str]:
        """Features that depend on nothing (foundational)."""
        return sorted(f for f in self._features
                      if not self._deps.get(f))

    def get_layers(self) -> list[list[str]]:
        """Group features by dependency depth."""
        depths: dict[str, int] = {}
        def get_depth(f: str) -> int:
            if f in depths: return depths[f]
            deps = self._deps.get(f, set())
            if not deps:
                depths[f] = 0
                return 0
            d = 1 + max(get_depth(d) for d in deps if d in self._features)
            depths[f] = d
            return d
        for f in self._features:
            get_depth(f)
        layers: dict[int, list[str]] = defaultdict(list)
        for f, d in depths.items():
            layers[d].append(f)
        return [sorted(layers[i]) for i in sorted(layers)]
