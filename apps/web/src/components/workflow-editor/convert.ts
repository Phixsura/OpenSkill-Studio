// Pure conversion functions between the workflow definition JSONB shape and
// React Flow's nodes/edges. No React imports — unit-testable.
// Round-trip invariant: toDefinition(def, ...toReactFlow(def)) preserves steps/edges.

import dagre from "dagre";
import type { Edge, Node } from "@xyflow/react";

import type { EdgeDef, StepDef, WorkflowDefinition } from "./types";

export type StepNodeData = { step: StepDef };

export function toReactFlow(def: WorkflowDefinition): {
  nodes: Node<StepNodeData>[];
  edges: Edge[];
} {
  const positions = def.ui?.positions ?? {};
  const nodes: Node<StepNodeData>[] = def.steps.map((step, index) => {
    const pos = positions[step.id] ?? [index * 280, 80];
    return {
      id: step.id,
      type: "stepNode",
      position: { x: pos[0], y: pos[1] },
      data: { step },
    };
  });
  const edges: Edge[] = def.edges.map((e) => ({
    id: e.id,
    source: e.from_step,
    target: e.to_step,
    sourceHandle: e.from_port,
    targetHandle: e.to_port,
  }));
  return { nodes, edges };
}

export function toDefinition(
  prev: WorkflowDefinition,
  nodes: Node<StepNodeData>[],
  edges: Edge[],
): WorkflowDefinition {
  // Preserve original step order where possible; append new nodes at the end
  const nodeById = new Map(nodes.map((n) => [n.id, n]));
  const orderedIds: string[] = [];
  for (const step of prev.steps) {
    if (nodeById.has(step.id)) orderedIds.push(step.id);
  }
  for (const node of nodes) {
    if (!orderedIds.includes(node.id)) orderedIds.push(node.id);
  }

  const steps: StepDef[] = orderedIds
    .map((id) => nodeById.get(id))
    .filter((n): n is Node<StepNodeData> => n !== undefined)
    .map((n) => n.data.step);

  const edgeDefs: EdgeDef[] = edges.map((e) => ({
    id:
      e.id && !e.id.startsWith("xy-edge")
        ? e.id
        : `e_${e.source}_${e.sourceHandle ?? ""}_${e.target}_${e.targetHandle ?? ""}`,
    from_step: e.source,
    from_port: e.sourceHandle ?? "",
    to_step: e.target,
    to_port: e.targetHandle ?? "",
  }));

  const positions: Record<string, [number, number]> = {};
  for (const node of nodes) {
    positions[node.id] = [Math.round(node.position.x), Math.round(node.position.y)];
  }

  return {
    ...prev,
    steps,
    edges: edgeDefs,
    ui: { ...prev.ui, positions },
  };
}

/** Auto-arrange steps left-to-right with dagre. Returns a new definition. */
export function autoLayout(def: WorkflowDefinition): WorkflowDefinition {
  const g = new dagre.graphlib.Graph();
  g.setGraph({ rankdir: "LR", nodesep: 60, ranksep: 120 });
  g.setDefaultEdgeLabel(() => ({}));
  for (const step of def.steps) {
    g.setNode(step.id, { width: 240, height: 120 });
  }
  for (const edge of def.edges) {
    g.setEdge(edge.from_step, edge.to_step);
  }
  dagre.layout(g);
  const positions: Record<string, [number, number]> = {};
  for (const step of def.steps) {
    const node = g.node(step.id);
    if (node) positions[step.id] = [Math.round(node.x), Math.round(node.y)];
  }
  return { ...def, ui: { ...def.ui, positions } };
}
