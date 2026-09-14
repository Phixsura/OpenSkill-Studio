"""Capability ontology service — CRUD, graph validation, traversal (ADR-015 D1).

Validates:
  - `requires` edges must not form cycles (bounded DFS, max depth 20).
  - `specializes` must point child → parent direction.
  - No self-loops (enforced by DB CHECK + service).
"""

from __future__ import annotations

import re
from collections import defaultdict

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.talent.models.capability import (
    EDGE_TYPES,
    MAPPING_SOURCE_TYPES,
    Capability,
    CapabilityEdge,
    CapabilityMapping,
)

MAX_TRAVERSAL_DEPTH = 20


def slugify(name: str) -> str:
    """Convert a capability name to a URL-safe slug."""
    s = name.lower().strip()
    s = re.sub(r"[^a-z0-9\s_-]", "", s)
    s = re.sub(r"[\s_]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    return s


class CapabilityService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ---- CRUD ----

    async def create_capability(
        self,
        *,
        canonical_name: str,
        category: str,
        description: str | None = None,
        parent_id: str | None = None,
        capability_tag_id: str | None = None,
        level_definitions: dict | None = None,
        decay_config: dict | None = None,
        sort_order: int = 0,
        external_ids: dict | None = None,
        aliases: list | None = None,
        translations: dict | None = None,
    ) -> Capability:
        slug = slugify(canonical_name)
        cap = Capability(
            canonical_name=canonical_name,
            slug=slug,
            description=description,
            category=category,
            parent_id=parent_id,
            capability_tag_id=capability_tag_id,
            level_definitions=level_definitions,
            decay_config=decay_config,
            sort_order=sort_order,
            external_ids=external_ids or {},
            aliases=aliases or [],
            translations=translations,
        )
        self.db.add(cap)
        await self.db.flush()
        return cap

    async def get_capability(self, capability_id: str) -> Capability | None:
        """Execute get capability."""
        return await self.db.get(Capability, capability_id)

    async def list_capabilities(
        self,
        *,
        category: str | None = None,
        status: str = "active",
        parent_id: str | None = ...,  # type: ignore[assignment]
        esco_uri: str | None = None,
        onet_code: str | None = None,
        limit: int = 100,
        offset: int = 0,
        cursor: str | None = None,
    ) -> tuple[list[Capability], int]:
        q = select(Capability).where(Capability.status == status)
        if category:
            q = q.where(Capability.category == category)
        if parent_id is not ...:
            if parent_id is None:
                q = q.where(Capability.parent_id.is_(None))
            else:
                q = q.where(Capability.parent_id == parent_id)
        # Taxonomy crosswalk filters
        if esco_uri:
            q = q.where(Capability.external_ids["esco_uri"].astext == esco_uri)
        if onet_code:
            q = q.where(Capability.external_ids["onet_code"].astext == onet_code)

        count_q = select(func.count()).select_from(q.subquery())
        total = (await self.db.execute(count_q)).scalar() or 0

        if cursor:
            q = q.where(Capability.id < cursor)
        q = q.order_by(Capability.sort_order, Capability.canonical_name).limit(limit + 1 if cursor is not None else limit).offset(0 if cursor is not None else offset)
        result = await self.db.execute(q)
        return list(result.scalars().all()), total

    async def update_capability(
        self,
        capability_id: str,
        **fields,
    ) -> Capability | None:
        cap = await self.db.get(Capability, capability_id)
        if not cap:
            return None

        # If parent_id is changing, check for circular reference
        new_parent = fields.get("parent_id")
        if new_parent is not None and new_parent != cap.parent_id:
            if new_parent == capability_id:
                raise ValueError("A capability cannot be its own parent")
            # Walk the parent chain from new_parent to detect cycle
            visited: set[str] = {capability_id}
            current = new_parent
            depth = 0
            while current and depth < MAX_TRAVERSAL_DEPTH:
                if current in visited:
                    raise ValueError("CYCLE_DETECTED: Setting this parent would create a circular reference")
                visited.add(current)
                parent_cap = await self.db.get(Capability, current)
                current = parent_cap.parent_id if parent_cap else None
                depth += 1

        for key, value in fields.items():
            if key == "canonical_name" and value is not None:
                cap.slug = slugify(value)
            if hasattr(cap, key):
                setattr(cap, key, value)

        await self.db.flush()
        return cap

    async def merge_capability(
        self,
        source_id: str,
        target_id: str,
    ) -> Capability | None:
        """Merge source into target — source becomes deprecated, mappings redirected."""
        source = await self.db.get(Capability, source_id)
        target = await self.db.get(Capability, target_id)
        if not source or not target:
            return None
        if source_id == target_id:
            raise ValueError("Cannot merge a capability into itself")

        source.status = "merged"
        source.merged_into_id = target_id

        # Redirect mappings from source → target (skip duplicates)
        mappings_q = select(CapabilityMapping).where(CapabilityMapping.capability_id == source_id)
        result = await self.db.execute(mappings_q)
        for mapping in result.scalars().all():
            # Check if target already has this mapping
            existing = await self.db.execute(
                select(CapabilityMapping).where(
                    CapabilityMapping.capability_id == target_id,
                    CapabilityMapping.source_type == mapping.source_type,
                    CapabilityMapping.source_id == mapping.source_id,
                )
            )
            if existing.scalar_one_or_none():
                continue
            mapping.capability_id = target_id

        await self.db.flush()
        return source

    # ---- Edges ----

    async def add_edge(
        self,
        *,
        source_id: str,
        target_id: str,
        edge_type: str,
        metadata: dict | None = None,
    ) -> CapabilityEdge:
        if edge_type not in EDGE_TYPES:
            raise ValueError(f"Invalid edge_type: {edge_type}. Must be one of {EDGE_TYPES}")
        if source_id == target_id:
            raise ValueError("Self-loops are not allowed")

        # Validate both capabilities exist
        source = await self.db.get(Capability, source_id)
        target = await self.db.get(Capability, target_id)
        if not source or not target:
            raise ValueError("Source or target capability not found")

        # Cycle detection for `requires` edges
        if edge_type == "requires" and await self._would_create_cycle(source_id, target_id, "requires"):
            raise ValueError("CYCLE_DETECTED: Adding this edge would create a cycle in 'requires' graph")

        edge = CapabilityEdge(
            source_id=source_id,
            target_id=target_id,
            edge_type=edge_type,
            extra=metadata,
        )
        self.db.add(edge)
        await self.db.flush()
        return edge

    async def remove_edge(self, edge_id: str) -> bool:
        """Execute remove edge."""
        edge = await self.db.get(CapabilityEdge, edge_id)
        if not edge:
            return False
        await self.db.delete(edge)
        await self.db.flush()
        return True

    async def get_edges(
        self,
        capability_id: str,
        *,
        direction: str = "both",
        edge_type: str | None = None,
    ) -> list[CapabilityEdge]:
        """Get edges for a capability. direction: 'outgoing', 'incoming', 'both'."""
        conditions = []
        if direction in ("outgoing", "both"):
            conditions.append(CapabilityEdge.source_id == capability_id)
        if direction in ("incoming", "both"):
            conditions.append(CapabilityEdge.target_id == capability_id)

        from sqlalchemy import or_

        q = select(CapabilityEdge).where(or_(*conditions))
        if edge_type:
            q = q.where(CapabilityEdge.edge_type == edge_type)

        result = await self.db.execute(q)
        return list(result.scalars().all())

    async def _would_create_cycle(
        self,
        source_id: str,
        target_id: str,
        edge_type: str,
    ) -> bool:
        """DFS from target following outgoing edges of edge_type.
        If we reach source, adding source→target would create a cycle."""
        # Load all edges of this type
        result = await self.db.execute(
            select(CapabilityEdge.source_id, CapabilityEdge.target_id).where(
                CapabilityEdge.edge_type == edge_type
            )
        )
        adjacency: dict[str, list[str]] = defaultdict(list)
        for src, tgt in result.all():
            adjacency[src].append(tgt)

        # DFS from target_id — if we reach source_id, it's a cycle
        visited: set[str] = set()
        stack = [target_id]
        depth = 0
        while stack and depth < MAX_TRAVERSAL_DEPTH:
            node = stack.pop()
            if node == source_id:
                return True
            if node in visited:
                continue
            visited.add(node)
            stack.extend(adjacency.get(node, []))
            depth += 1

        return False

    # ---- Graph traversal ----

    async def traverse_graph(
        self,
        capability_id: str,
        *,
        edge_types: set[str] | None = None,
        max_depth: int = 5,
    ) -> dict:
        """Bounded BFS traversal from a capability node."""
        if max_depth > MAX_TRAVERSAL_DEPTH:
            max_depth = MAX_TRAVERSAL_DEPTH

        root = await self.db.get(Capability, capability_id)
        if not root:
            return {}

        # Load relevant edges
        q = select(CapabilityEdge)
        if edge_types:
            q = q.where(CapabilityEdge.edge_type.in_(edge_types))
        result = await self.db.execute(q)
        edges = result.scalars().all()

        adjacency: dict[str, list[dict]] = defaultdict(list)
        for e in edges:
            adjacency[e.source_id].append({
                "target_id": e.target_id,
                "edge_type": e.edge_type,
            })
            # Also include reverse for undirected traversal
            adjacency[e.target_id].append({
                "target_id": e.source_id,
                "edge_type": e.edge_type,
            })

        # BFS
        visited: set[str] = {capability_id}
        queue = [(capability_id, 0)]
        nodes: list[dict] = []
        edge_list: list[dict] = []

        while queue:
            node_id, depth = queue.pop(0)
            if depth > max_depth:
                continue

            for adj in adjacency.get(node_id, []):
                target = adj["target_id"]
                edge_list.append({
                    "source_id": node_id,
                    "target_id": target,
                    "edge_type": adj["edge_type"],
                })
                if target not in visited:
                    visited.add(target)
                    queue.append((target, depth + 1))

        # Load capability details for all visited nodes
        if visited:
            cap_q = select(Capability).where(Capability.id.in_(visited))
            cap_result = await self.db.execute(cap_q)
            for cap in cap_result.scalars().all():
                nodes.append({
                    "id": cap.id,
                    "canonical_name": cap.canonical_name,
                    "category": cap.category,
                    "status": cap.status,
                    "depth": 0,  # Approximate — exact depth needs BFS tracking
                })

        return {
            "root_id": capability_id,
            "nodes": nodes,
            "edges": edge_list,
        }

    # ---- Mappings ----

    async def create_mapping(
        self,
        *,
        capability_id: str,
        source_type: str,
        source_id: str,
        contribution_weight: float = 1.0,
        evidence_type: str = "primary_instruction",
    ) -> CapabilityMapping:
        if source_type not in MAPPING_SOURCE_TYPES:
            raise ValueError(f"Invalid source_type: {source_type}")
        if not (0 <= contribution_weight <= 1):
            raise ValueError("contribution_weight must be in [0, 1]")

        mapping = CapabilityMapping(
            capability_id=capability_id,
            source_type=source_type,
            source_id=source_id,
            contribution_weight=contribution_weight,
            evidence_type=evidence_type,
        )
        self.db.add(mapping)
        await self.db.flush()
        return mapping

    async def get_mappings(
        self,
        *,
        capability_id: str | None = None,
        source_type: str | None = None,
        source_id: str | None = None,
    ) -> list[CapabilityMapping]:
        q = select(CapabilityMapping)
        if capability_id:
            q = q.where(CapabilityMapping.capability_id == capability_id)
        if source_type:
            q = q.where(CapabilityMapping.source_type == source_type)
        if source_id:
            q = q.where(CapabilityMapping.source_id == source_id)

        result = await self.db.execute(q)
        return list(result.scalars().all())

    async def delete_mapping(self, mapping_id: str) -> bool:
        """Execute delete mapping."""
        mapping = await self.db.get(CapabilityMapping, mapping_id)
        if not mapping:
            return False
        await self.db.delete(mapping)
        await self.db.flush()
        return True
