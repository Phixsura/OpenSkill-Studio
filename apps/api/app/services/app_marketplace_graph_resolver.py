"""Graph Resolver — resolve extension relationship graphs.

Maps relationships between extensions (depends-on, extends, replaces,
integrates-with) and provides graph traversal and analysis.
"""
from __future__ import annotations
from collections import defaultdict
from dataclasses import dataclass
from enum import Enum


class RelationType(str, Enum):
    DEPENDS_ON = "depends_on"
    EXTENDS = "extends"
    REPLACES = "replaces"
    INTEGRATES_WITH = "integrates_with"
    CONFLICTS_WITH = "conflicts_with"


@dataclass
class Relationship:
    source: str
    target: str
    relation: RelationType


class ExtensionGraphResolver:
    """Resolves and analyzes extension relationship graphs."""

    def __init__(self):
        self._edges: list[Relationship] = []
        self._adj: dict[str, list[Relationship]] = defaultdict(list)
        self._reverse: dict[str, list[Relationship]] = defaultdict(list)

    def add_relationship(self, source: str, target: str, relation: RelationType) -> Relationship:
        rel = Relationship(source=source, target=target, relation=relation)
        self._edges.append(rel)
        self._adj[source].append(rel)
        self._reverse[target].append(rel)
        return rel

    def get_outgoing(self, extension_id: str, relation: RelationType | None = None) -> list[Relationship]:
        rels = self._adj.get(extension_id, [])
        if relation:
            rels = [r for r in rels if r.relation == relation]
        return rels

    def get_incoming(self, extension_id: str, relation: RelationType | None = None) -> list[Relationship]:
        rels = self._reverse.get(extension_id, [])
        if relation:
            rels = [r for r in rels if r.relation == relation]
        return rels

    def get_dependencies(self, extension_id: str) -> list[str]:
        """Get all extensions this one depends on (transitive)."""
        visited = set()
        def _walk(eid: str) -> None:
            for rel in self._adj.get(eid, []):
                if rel.relation == RelationType.DEPENDS_ON and rel.target not in visited:
                    visited.add(rel.target)
                    _walk(rel.target)
        _walk(extension_id)
        return sorted(visited)

    def get_dependents(self, extension_id: str) -> list[str]:
        """Get all extensions that depend on this one (transitive)."""
        visited = set()
        def _walk(eid: str) -> None:
            for rel in self._reverse.get(eid, []):
                if rel.relation == RelationType.DEPENDS_ON and rel.source not in visited:
                    visited.add(rel.source)
                    _walk(rel.source)
        _walk(extension_id)
        return sorted(visited)

    def impact_analysis(self, extension_id: str) -> dict:
        """Analyze the impact of removing/changing an extension."""
        dependents = self.get_dependents(extension_id)
        integrations = [r.source for r in self.get_incoming(extension_id, RelationType.INTEGRATES_WITH)]
        replacements = [r.source for r in self.get_incoming(extension_id, RelationType.REPLACES)]
        return {
            "extension_id": extension_id,
            "direct_dependents": len(self.get_incoming(extension_id, RelationType.DEPENDS_ON)),
            "transitive_dependents": len(dependents),
            "dependents": dependents,
            "integrations": integrations,
            "can_be_replaced_by": replacements,
            "high_impact": len(dependents) >= 5,
        }

    def get_all_nodes(self) -> list[str]:
        nodes = set()
        for rel in self._edges:
            nodes.add(rel.source)
            nodes.add(rel.target)
        return sorted(nodes)
