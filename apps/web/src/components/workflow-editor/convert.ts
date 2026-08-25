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

/** Detect a positional 1:1 port rename between two port-name lists.
 *
 * Lists must be the same length with EXACTLY one index differing. Comparing
 * POSITIONALLY (not as Sets) matters: a rename keystroke can pass through a
 * sibling port's exact name ('in2' → backspace → 'in' next to a port 'in'),
 * and a Set collapses that duplicate — the rename went undetected and the
 * edge filter silently dropped the port's edges, with no way to restore
 * them. Length changes and multi-index diffs are not renames — the caller
 * then keeps edges for ports whose names still exist and drops only edges
 * whose port vanished.
 *
 * One extra guard: when the renamed-FROM name still exists at another index
 * (renaming away from a transient duplicate), edges reference ports by NAME
 * so a rewrite would drag the sibling port's edges along with it — treat
 * that as no-rename and let the keep-if-name-still-exists filter preserve
 * every edge instead. */
function detectPortRename(
  prevPorts: string[],
  newPorts: string[],
): { from: string; to: string } | null {
  if (prevPorts.length !== newPorts.length) return null;
  let rename: { from: string; to: string } | null = null;
  for (let i = 0; i < prevPorts.length; i++) {
    const from = prevPorts[i];
    const to = newPorts[i];
    if (from === undefined || to === undefined || from === to) continue;
    if (rename) return null; // more than one index changed
    rename = { from, to };
  }
  if (rename && newPorts.includes(rename.from)) return null;
  return rename;
}

/** Apply a step edit to the definition, cascading port renames/removals.
 *
 * A positional 1:1 port change is a RENAME (every keystroke in the port name
 * field is one): edges and workflow outputs referencing the old name are
 * REWRITTEN to the new name — dropping them would silently destroy the
 * user's connections one keystroke at a time. Anything else (pure removal,
 * length change, multi-port changes) keeps edges for ports whose names still
 * exist and drops only edges whose port vanished.
 * Pure function — unit-testable without React. */
export function applyStepUpdate(def: WorkflowDefinition, updated: StepDef): WorkflowDefinition {
  const prev = def.steps.find((s) => s.id === updated.id);
  const newInputPorts = new Set(updated.inputs.map((p) => p.port));
  const newOutputPorts = new Set(updated.outputs.map((p) => p.port));

  const inputRename = detectPortRename(
    (prev?.inputs ?? []).map((p) => p.port),
    updated.inputs.map((p) => p.port),
  );
  const outputRename = detectPortRename(
    (prev?.outputs ?? []).map((p) => p.port),
    updated.outputs.map((p) => p.port),
  );

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
    // Prune only rows whose selected port vanished from this step. An
    // in-progress row with from_port === "" (user clicked "Add output" but
    // hasn't picked a port yet) references a still-existing step and must
    // survive unrelated step edits — "" is never a real port name.
    .filter(
      (o) =>
        !(o.from_step === updated.id && o.from_port !== "" && !newOutputPorts.has(o.from_port)),
    );

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
