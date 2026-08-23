"use client";

import { useCallback } from "react";
import {
  Background,
  Controls,
  MiniMap,
  ReactFlow,
} from "@xyflow/react";
import type {
  Connection,
  Edge,
  EdgeChange,
  Node,
  NodeChange,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";

import type { StepNodeData } from "./convert";
import { StepNode } from "./step-node";
import type { WorkflowDefinition } from "./types";
import { COERCIBLE } from "./types";

const nodeTypes = { stepNode: StepNode };

interface Props {
  definition: WorkflowDefinition;
  nodes: Node<StepNodeData>[];
  edges: Edge[];
  onNodesChange: (changes: NodeChange<Node<StepNodeData>>[]) => void;
  onEdgesChange: (changes: EdgeChange<Edge>[]) => void;
  onConnect: (connection: Connection) => void;
  onSelectStep: (stepId: string | null) => void;
}

export function CanvasView({
  definition,
  nodes,
  edges,
  onNodesChange,
  onEdgesChange,
  onConnect,
  onSelectStep,
}: Props) {
  // Client-side pre-check mirroring the backend coercion matrix; the server
  // remains the authority at save time.
  const isValidConnection = useCallback(
    (conn: Connection | Edge) => {
      const source = definition.steps.find((s) => s.id === conn.source);
      const target = definition.steps.find((s) => s.id === conn.target);
      if (!source || !target) return false;
      const srcPort = source.outputs.find((p) => p.port === conn.sourceHandle);
      const dstPort = target.inputs.find((p) => p.port === conn.targetHandle);
      if (!srcPort || !dstPort) return false;
      // Fan-in 1: an input port that already has an incoming edge cannot
      // take another — the runtime resolves edges last-writer-wins, so a
      // second feed would be silently nondeterministic.
      const alreadyFed = edges.some(
        (e) => e.target === conn.target && e.targetHandle === conn.targetHandle,
      );
      if (alreadyFed) return false;
      return COERCIBLE[srcPort.type]?.includes(dstPort.type) ?? false;
    },
    [definition, edges],
  );

  return (
    <div className="h-[600px] rounded-lg border">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        isValidConnection={isValidConnection}
        onNodeClick={(_, node) => onSelectStep(node.id)}
        onPaneClick={() => onSelectStep(null)}
        fitView
        proOptions={{ hideAttribution: true }}
      >
        <Background />
        <Controls />
        <MiniMap pannable zoomable />
      </ReactFlow>
    </div>
  );
}
