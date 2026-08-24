// Pure conversion functions between the workflow definition JSONB shape and
// React Flow's nodes/edges. No React imports — unit-testable.
// Round-trip invariant: toDefinition(def, ...toReactFlow(def)) preserves steps/edges.

import dagre from "dagre";
import type { Edge, Node } from "@xyflow/react";

import type { EdgeDef, StepDef, WorkflowDefinition } from "./types";
import { normalizePosition } from "./types";

export type StepNodeData = { step: StepDef };

export function toReactFlow(def: WorkflowDefinition): {
  nodes: Node<StepNodeData>[];
  edges: Edge[];
} {
  const positions = def.ui?.positions ?? {};
  const nodes: Node<StepNodeData>[] = def.steps.map((step, index) => {
    // The ui block is excluded from backend validation, so a stored
    // position can be arbitrary junk — a NaN position blanks the canvas.
    const pos = normalizePosition(positions[step.id]) ?? [index * 280, 80];
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
    // Join with '.' — step ids/ports contain '_' themselves, so an
    // underscore-joined id is ambiguous (a/b_c collides with a_b/c) and
    // collisions get rejected server-side as WF_DUPLICATE_EDGE_ID.
    // '.' is excluded from the id charset (^[a-z][a-z0-9_]*$), so this
    // encoding is unambiguous.
    id:
      e.id && !e.id.startsWith("xy-edge")
        ? e.id
        : `e_${e.source}.${e.sourceHandle ?? ""}.${e.target}.${e.targetHandle ?? ""}`,
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

/** Apply a step edit to the definition, cascading port renames/removals.
 *
 * A 1:1 gone/added port pair is a RENAME (every keystroke in the port name
 * field is one): edges and workflow outputs referencing the old name are
 * REWRITTEN to the new name — dropping them would silently destroy the
 * user's connections one keystroke at a time. Anything else (pure removal,
 * multi-port changes) cascades removal the same way deleting a step does.
 * Pure function — unit-testable without React. */
export function applyStepUpdate(def: WorkflowDefinition, updated: StepDef): WorkflowDefinition {
  const prev = def.steps.find((s) => s.id === updated.id);
  const prevInputPorts = new Set((prev?.inputs ?? []).map((p) => p.port));
  const prevOutputPorts = new Set((prev?.outputs ?? []).map((p) => p.port));
  const newInputPorts = new Set(updated.inputs.map((p) => p.port));
  const newOutputPorts = new Set(updated.outputs.map((p) => p.port));
  const goneInputs = new Set([...prevInputPorts].filter((p) => !newInputPorts.has(p)));
  const goneOutputs = new Set([...prevOutputPorts].filter((p) => !newOutputPorts.has(p)));
  const addedInputs = [...newInputPorts].filter((p) => !prevInputPorts.has(p));
  const addedOutputs = [...newOutputPorts].filter((p) => !prevOutputPorts.has(p));

  const inputRename =
    goneInputs.size === 1 && addedInputs.length === 1
      ? { from: [...goneInputs][0] as string, to: addedInputs[0] as string }
      : null;
  const outputRename =
    goneOutputs.size === 1 && addedOutputs.length === 1
      ? { from: [...goneOutputs][0] as string, to: addedOutputs[0] as string }
      : null;

  const edges = def.edges
    .map((e) => {
      let next = e;
      if (inputRename && e.to_step === updated.id && e.to_port === inputRename.from) {
        next = { ...next, to_port: inputRename.to };
      }
      if (outputRename && e.from_step === updated.id && e.from_port === outputRename.from) {
        next = { ...next, from_port: outputRename.to };
      }
      return next;
    })
    .filter(
      (e) =>
        !(e.to_step === updated.id && !newInputPorts.has(e.to_port)) &&
        !(e.from_step === updated.id && !newOutputPorts.has(e.from_port)),
    );
  const outputs = def.outputs
    .map((o) =>
      outputRename && o.from_step === updated.id && o.from_port === outputRename.from
        ? { ...o, from_port: outputRename.to }
        : o,
    )
    .filter((o) => !(o.from_step === updated.id && !newOutputPorts.has(o.from_port)));

  return {
    ...def,
    steps: def.steps.map((s) => (s.id === updated.id ? updated : s)),
    edges,
    outputs,
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
