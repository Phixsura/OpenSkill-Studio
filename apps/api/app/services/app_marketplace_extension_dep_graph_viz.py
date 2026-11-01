"""Dependency Graph Visualizer — compute layout for dependency visualization.

Implements:
- DAG layer assignment (Sugiyama-style)
- Cross-minimization between layers (barycenter heuristic)
- Node positioning for rendering
- Cycle detection and back-edge marking
- Graph metrics (depth, width, fan-in/fan-out)
"""
from __future__ import annotations
from dataclasses import dataclass, field
from collections import deque, defaultdict


@dataclass
class GraphNodeLayout:
    node_id: str
    label: str
    layer: int
    x: float = 0
    y: float = 0
    fan_in: int = 0
    fan_out: int = 0


@dataclass
class GraphEdgeLayout:
    source: str
    target: str
    back_edge: bool = False  # cycle indicator


@dataclass
class GraphLayout:
    nodes: list[GraphNodeLayout]
    edges: list[GraphEdgeLayout]
    layers: int = 0
    max_width: int = 0
    has_cycles: bool = False


class DepGraphVizService:
    def compute_layout(self, nodes: dict[str, str],
                       edges: list[tuple[str, str]]) -> GraphLayout:
        """Compute graph layout for visualization.
        nodes: {id: label}, edges: [(source, target)]"""
        adj: dict[str, list[str]] = defaultdict(list)
        rev: dict[str, list[str]] = defaultdict(list)

        for src, tgt in edges:
            adj[src].append(tgt)
            rev[tgt].append(src)

        # Detect cycles
        back_edges = self._find_back_edges(set(nodes), adj)
        has_cycles = len(back_edges) > 0

        # Remove back edges for layering
        clean_edges = [(s, t) for s, t in edges if (s, t) not in back_edges]
        clean_adj: dict[str, list[str]] = defaultdict(list)
        clean_rev: dict[str, list[str]] = defaultdict(list)
        for s, t in clean_edges:
            clean_adj[s].append(t)
            clean_rev[t].append(s)

        # Layer assignment (longest path from sources)
        layers = self._assign_layers(set(nodes), clean_adj, clean_rev)

        # Position nodes within layers
        node_layouts = []
        layer_nodes: dict[int, list[str]] = defaultdict(list)
        for nid, layer in layers.items():
            layer_nodes[layer].append(nid)

        # Cross minimization (barycenter heuristic)
        for layer_idx in sorted(layer_nodes):
            if layer_idx > 0:
                self._minimize_crossings(layer_nodes, layer_idx, clean_adj, clean_rev)

        # Assign x/y positions
        max_width = 0
        for layer_idx in sorted(layer_nodes):
            nids = layer_nodes[layer_idx]
            max_width = max(max_width, len(nids))
            for i, nid in enumerate(nids):
                x = (i + 0.5) * (100 / max(1, len(nids)))
                y = layer_idx * 80
                node_layouts.append(GraphNodeLayout(
                    node_id=nid, label=nodes.get(nid, nid),
                    layer=layer_idx, x=round(x, 1), y=y,
                    fan_in=len(rev.get(nid, [])),
                    fan_out=len(adj.get(nid, []))))

        edge_layouts = [GraphEdgeLayout(s, t, (s, t) in back_edges)
                        for s, t in edges]

        return GraphLayout(nodes=node_layouts, edges=edge_layouts,
                           layers=max(layers.values()) + 1 if layers else 0,
                           max_width=max_width, has_cycles=has_cycles)

    def _assign_layers(self, nodes: set[str], adj: dict[str, list[str]],
                       rev: dict[str, list[str]]) -> dict[str, int]:
        """Longest-path layering."""
        layers: dict[str, int] = {}

        def dfs(node: str) -> int:
            if node in layers:
                return layers[node]
            parents = rev.get(node, [])
            if not parents:
                layers[node] = 0
                return 0
            depth = max(dfs(p) for p in parents) + 1
            layers[node] = depth
            return depth

        for node in nodes:
            dfs(node)
        return layers

    def _minimize_crossings(self, layer_nodes: dict[int, list[str]],
                             layer_idx: int, adj: dict, rev: dict) -> None:
        """Barycenter heuristic: order nodes by average position of predecessors."""
        prev_layer = layer_nodes.get(layer_idx - 1, [])
        if not prev_layer:
            return
        pos = {nid: i for i, nid in enumerate(prev_layer)}

        def barycenter(nid: str) -> float:
            parents = rev.get(nid, [])
            parent_positions = [pos[p] for p in parents if p in pos]
            return sum(parent_positions) / len(parent_positions) if parent_positions else 0

        layer_nodes[layer_idx].sort(key=barycenter)

    def _find_back_edges(self, nodes: set[str],
                          adj: dict[str, list[str]]) -> set[tuple[str, str]]:
        """Find back edges (cycles) via DFS coloring."""
        WHITE, GRAY, BLACK = 0, 1, 2
        color = {n: WHITE for n in nodes}
        back_edges = set()

        def dfs(u: str):
            color[u] = GRAY
            for v in adj.get(u, []):
                if v not in color:
                    continue
                if color[v] == GRAY:
                    back_edges.add((u, v))
                elif color[v] == WHITE:
                    dfs(v)
            color[u] = BLACK

        for node in nodes:
            if color[node] == WHITE:
                dfs(node)
        return back_edges

    def get_metrics(self, layout: GraphLayout) -> dict:
        """Compute graph metrics."""
        if not layout.nodes:
            return {"nodes": 0, "edges": 0}
        max_fan_in = max(n.fan_in for n in layout.nodes)
        max_fan_out = max(n.fan_out for n in layout.nodes)
        bottleneck = [n.node_id for n in layout.nodes if n.fan_in == max_fan_in]
        return {
            "nodes": len(layout.nodes),
            "edges": len(layout.edges),
            "layers": layout.layers,
            "max_width": layout.max_width,
            "has_cycles": layout.has_cycles,
            "max_fan_in": max_fan_in,
            "max_fan_out": max_fan_out,
            "bottleneck_nodes": bottleneck,
        }
